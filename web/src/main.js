import './style.css'
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js'

const WS_URL = 'ws://127.0.0.1:8765'

// ===== DOM Elements =====
const container = document.getElementById('app')
const loadingScreen = document.getElementById('loading-screen')
const loaderStatus = document.querySelector('.loader-status')

// ===== Theme Configuration =====
const themes = {
  dark: { background: 0x0a0a0f, grid: 0x333344, ambient: 0x404050 },
  light: { background: 0xf8fafc, grid: 0xcccccc, ambient: 0xffffff },
  blueprint: { background: 0x0d1b2a, grid: 0x1b4b6b, ambient: 0x3d5a80 }
}

let currentTheme = 'dark'

// ===== Scene Setup =====
const scene = new THREE.Scene()
scene.background = new THREE.Color(themes[currentTheme].background)
scene.fog = new THREE.Fog(themes[currentTheme].background, 8, 25)

// ===== Camera =====
const camera = new THREE.PerspectiveCamera(
  50,
  window.innerWidth / window.innerHeight,
  0.1,
  100
)
camera.position.set(3, 2.5, 4)

// ===== Renderer =====
const renderer = new THREE.WebGLRenderer({
  antialias: true,
  powerPreference: 'high-performance'
})
renderer.setSize(window.innerWidth, window.innerHeight)
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
renderer.shadowMap.enabled = true
renderer.shadowMap.type = THREE.PCFSoftShadowMap
renderer.toneMapping = THREE.ACESFilmicToneMapping
renderer.toneMappingExposure = 1.2
container.appendChild(renderer.domElement)

// ===== Controls =====
const controls = new OrbitControls(camera, renderer.domElement)
controls.enableDamping = true
controls.dampingFactor = 0.05
controls.target.set(0, 0.8, 0)
controls.minDistance = 0.1
controls.maxDistance = 15
controls.maxPolarAngle = Math.PI * 0.85

// ===== Lighting =====
const ambientLight = new THREE.AmbientLight(0xffffff, 0.4)
scene.add(ambientLight)

const hemisphereLight = new THREE.HemisphereLight(0xffffff, themes[currentTheme].ambient, 0.6)
scene.add(hemisphereLight)

const mainLight = new THREE.DirectionalLight(0xffffff, 1.2)
mainLight.position.set(5, 10, 7)
mainLight.castShadow = true
mainLight.shadow.mapSize.width = 2048
mainLight.shadow.mapSize.height = 2048
mainLight.shadow.camera.near = 0.5
mainLight.shadow.camera.far = 30
mainLight.shadow.camera.left = -10
mainLight.shadow.camera.right = 10
mainLight.shadow.camera.top = 10
mainLight.shadow.camera.bottom = -10
mainLight.shadow.bias = -0.0001
scene.add(mainLight)

const fillLight = new THREE.DirectionalLight(0x8888ff, 0.3)
fillLight.position.set(-5, 5, -5)
scene.add(fillLight)

const rimLight = new THREE.DirectionalLight(0xff8844, 0.2)
rimLight.position.set(0, 3, -8)
scene.add(rimLight)

// ===== Grid =====
const grid = new THREE.GridHelper(20, 40, themes[currentTheme].grid, themes[currentTheme].grid)
grid.material.opacity = 0.3
grid.material.transparent = true
grid.visible = false
scene.add(grid)

// ===== Model Loading =====
const loader = new GLTFLoader()
let robot = null

// ===== Joint Configuration =====
// These names must exist in the exported GLB as Empty/pivot nodes.
const JOINTS = {
  basis: {
    nodeName: 'rotating_base_pivot',
    axis: 'y',
    invert: true,
    offsetDeg: 0,
  },
  main: {
    nodeName: 'main_arm_pivot',
    axis: 'z',
    invert: true,
    offsetDeg: 0,
  },
  fore: {
    nodeName: 'fore_arm_pivot',
    axis: 'z',
    invert: false,
    offsetDeg: 0,
  },
  wrist: {
    nodeName: 'wrist_pivot',
    axis: 'z',
    invert: true,
    offsetDeg: 0,
  },
}

const jointNodes = {}
const jointRestRotations = {}
const currentPose = {
  basis: 0,
  main: 0,
  fore: 0,
  wrist: 0,
}

let robotSocket = null
let reconnectTimer = null

function setupRobotJoints() {
  Object.entries(JOINTS).forEach(([key, cfg]) => {
    const node = robot.getObjectByName(cfg.nodeName)
    jointNodes[key] = node || null

    if (!node) {
      console.warn(`[joint missing] ${key} -> ${cfg.nodeName}`)
      return
    }

    node.rotation.order = 'XYZ'

    jointRestRotations[key] = {
      x: node.rotation.x,
      y: node.rotation.y,
      z: node.rotation.z,
    }

    console.log(`[joint found] ${key} -> ${cfg.nodeName}`, node)
  })
}

function applyJointAngle(jointKey, angleDeg) {
  const cfg = JOINTS[jointKey]
  const node = jointNodes[jointKey]
  const rest = jointRestRotations[jointKey]

  if (!cfg || !node || !rest) return

  const finalDeg = (cfg.invert ? -angleDeg : angleDeg) + cfg.offsetDeg
  const angleRad = THREE.MathUtils.degToRad(finalDeg)

  node.rotation.x = rest.x
  node.rotation.y = rest.y
  node.rotation.z = rest.z
  node.rotation[cfg.axis] = rest[cfg.axis] + angleRad
}

function applyRobotPose(pose) {
  currentPose.basis = pose.basis ?? currentPose.basis
  currentPose.main = pose.main ?? currentPose.main
  currentPose.fore = pose.fore ?? currentPose.fore
  currentPose.wrist = pose.wrist ?? currentPose.wrist

  applyJointAngle('basis', currentPose.basis)
  applyJointAngle('main', currentPose.main)
  applyJointAngle('fore', currentPose.fore)
  applyJointAngle('wrist', currentPose.wrist)

  updateJointDisplay({
    base: currentPose.basis,
    shoulder: currentPose.main,
    elbow: currentPose.fore,
    wrist: currentPose.wrist,
  })
}

function parseIncomingPose(raw) {
  try {
    if (typeof raw === 'string' && raw.trim().startsWith('{')) {
      const data = JSON.parse(raw)
      return {
        basis: Number(data.basis),
        main: Number(data.main),
        fore: Number(data.fore),
        wrist: Number(data.wrist),
      }
    }

    const parts = String(raw).split(',').map(v => Number(v.trim()))
    if (parts.length !== 4 || parts.some(v => Number.isNaN(v))) {
      return null
    }

    return {
      basis: parts[0],
      main: parts[1],
      fore: parts[2],
      wrist: parts[3],
    }
  } catch (err) {
    console.error('Failed to parse incoming pose:', raw, err)
    return null
  }
}

function connectRobotStream() {
  if (
    robotSocket &&
    (robotSocket.readyState === WebSocket.OPEN || robotSocket.readyState === WebSocket.CONNECTING)
  ) {
    return
  }

  robotSocket = new WebSocket(WS_URL)

  robotSocket.addEventListener('open', () => {
    console.log('WebSocket connected')
    setConnectionStatus(true)
  })

  robotSocket.addEventListener('message', (event) => {
    const pose = parseIncomingPose(event.data)
    if (!pose) return
    applyRobotPose(pose)
  })

  robotSocket.addEventListener('close', () => {
    console.warn('WebSocket disconnected')
    setConnectionStatus(false)

    clearTimeout(reconnectTimer)
    reconnectTimer = setTimeout(() => {
      connectRobotStream()
    }, 1000)
  })

  robotSocket.addEventListener('error', (err) => {
    console.error('WebSocket error:', err)
    robotSocket.close()
  })
}

loaderStatus.textContent = 'Loading 3D model...'

loader.load(
  '/models/robot-arm_digital-twin.glb',
  (gltf) => {
    robot = gltf.scene

    robot.traverse((obj) => {
      if (obj.isMesh) {
        obj.castShadow = true
        obj.receiveShadow = true

        if (obj.material) {
          obj.material.envMapIntensity = 0.5
        }
      }
    })

    scene.add(robot)
    setupRobotJoints()
    connectRobotStream()

    loaderStatus.textContent = 'Ready!'
    setTimeout(() => {
      loadingScreen.classList.add('hidden')
    }, 500)

    console.log('Model loaded successfully')
  },
  (progress) => {
    const percent = progress.total ? Math.round((progress.loaded / progress.total) * 100) : 0
    loaderStatus.textContent = `Loading model... ${percent}%`
  },
  (error) => {
    console.error('Failed to load model:', error)
    loaderStatus.textContent = 'Failed to load model'
  }
)

// ===== Animation Loop =====
function animate() {
  requestAnimationFrame(animate)
  controls.update()
  renderer.render(scene, camera)
}
animate()

// ===== Event Handlers =====
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight
  camera.updateProjectionMatrix()
  renderer.setSize(window.innerWidth, window.innerHeight)
})

document.getElementById('btn-toggle-grid').addEventListener('click', () => {
  grid.visible = !grid.visible
})

document.getElementById('toggle-autorotate').addEventListener('change', (e) => {
  controls.autoRotate = e.target.checked
  controls.autoRotateSpeed = 1.0
})

document.getElementById('toggle-shadows').addEventListener('change', (e) => {
  renderer.shadowMap.enabled = e.target.checked
  scene.traverse((obj) => {
    if (obj.isMesh) {
      obj.castShadow = e.target.checked
      obj.receiveShadow = e.target.checked
    }
  })
  renderer.render(scene, camera)
})

document.querySelectorAll('.theme-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.theme-btn').forEach(b => b.classList.remove('active'))
    btn.classList.add('active')

    const themeName = btn.dataset.theme
    currentTheme = themeName
    document.body.setAttribute('data-theme', themeName)

    const theme = themes[themeName]
    scene.background.setHex(theme.background)
    scene.fog.color.setHex(theme.background)
    grid.material.color.setHex(theme.grid)
    hemisphereLight.groundColor.setHex(theme.ambient)
  })
})

// ===== Joint Angle Display =====
function updateJointDisplay(jointData) {
  if (jointData.base !== undefined) {
    document.getElementById('joint-base').textContent = `${jointData.base.toFixed(1)}°`
  }
  if (jointData.shoulder !== undefined) {
    document.getElementById('joint-shoulder').textContent = `${jointData.shoulder.toFixed(1)}°`
  }
  if (jointData.elbow !== undefined) {
    document.getElementById('joint-elbow').textContent = `${jointData.elbow.toFixed(1)}°`
  }
  if (jointData.wrist !== undefined) {
    document.getElementById('joint-wrist').textContent = `${jointData.wrist.toFixed(1)}°`
  }
  if (jointData.gripper !== undefined) {
    document.getElementById('joint-gripper').textContent = `${jointData.gripper.toFixed(1)}%`
  }
}

// ===== Connection Status =====
function setConnectionStatus(connected) {
  const statusEl = document.getElementById('connection-status')
  const statusText = statusEl.querySelector('.status-text')

  if (connected) {
    statusEl.classList.add('connected')
    statusText.textContent = 'Connected'
  } else {
    statusEl.classList.remove('connected')
    statusText.textContent = 'Disconnected'
  }
}

window.leaderArmViewer = {
  updateJointDisplay,
  setConnectionStatus,
  getScene: () => scene,
  getCamera: () => camera,
  getRobot: () => robot,
  applyRobotPose,
  getJointNodes: () => jointNodes,
  getJointConfig: () => JOINTS,
}