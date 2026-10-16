import { Suspense, useRef, useState, useEffect, Component } from "react";
import { Canvas } from "@react-three/fiber";
import {
  useGLTF,
  useAnimations,
  OrbitControls,
  Center,
  ContactShadows,
} from "@react-three/drei";
import { LoaderCircle, AlertCircle, RotateCcw } from "lucide-react";
import "./Cow3D.css";

// Preload the local GLB model
useGLTF.preload("/models/farm_cow_animated_dairy_cattle.glb");

/**
 * Animated 3D Cow Model Component
 */
function CowModel({ currentAnim, onAnimationNamesLoaded }) {
  const group = useRef();
  const { scene, animations } = useGLTF("/models/farm_cow_animated_dairy_cattle.glb");
  const { actions, names } = useAnimations(animations, group);

  useEffect(() => {
    if (names && names.length > 0 && onAnimationNamesLoaded) {
      onAnimationNamesLoaded(names);
    }
  }, [names, onAnimationNamesLoaded]);

  useEffect(() => {
    if (!actions || !names || names.length === 0) return;

    // Determine target animation: requested or fallback to idle1 / first
    const targetName =
      currentAnim && actions[currentAnim]
        ? currentAnim
        : actions["Armature|idle1"]
        ? "Armature|idle1"
        : actions["Armature|idle2"]
        ? "Armature|idle2"
        : names[0];

    const action = actions[targetName];
    if (action) {
      // Fade out any other playing animations
      Object.values(actions).forEach((act) => {
        if (act !== action && act.isRunning()) {
          act.fadeOut(0.4);
        }
      });

      action.reset().fadeIn(0.4).play();
    }

    return () => {
      if (action) action.fadeOut(0.3);
    };
  }, [actions, names, currentAnim]);

  return (
    <group ref={group} dispose={null}>
      <Center position={[0, 0, 0]}>
        {/* Scale cow to fit prominently in hero viewport with ample whitespace */}
        <primitive object={scene} scale={1.85} />
      </Center>
    </group>
  );
}

/**
 * React Error Boundary for 3D Scene
 */
class ThreeErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.warn("Cow3D Canvas encountered an issue:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="cow-3d-error-fallback">
          <div className="error-icon-wrap">
            <AlertCircle size={32} />
          </div>
          <h3>3D Model Rendering Fallback</h3>
          <p>
            WebGL accelerated rendering is temporarily constrained on your
            device.
          </p>
          <button
            className="retry-3d-btn"
            onClick={() => this.setState({ hasError: false })}
          >
            <RotateCcw size={15} />
            <span>Retry 3D View</span>
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

/**
 * Main Interactive Cow3D Component (Clean & Stationary by default)
 */
export default function Cow3D() {
  const [selectedAnim] = useState("Armature|idle1");
  const controlsRef = useRef();

  return (
    <div className="cow-3d-wrapper" aria-label="Interactive 3D model of cow">
      {/* 3D Canvas Container */}
      <div className="canvas-container">
        <ThreeErrorBoundary>
          <Suspense
            fallback={
              <div className="cow-3d-loading-overlay">
                <LoaderCircle size={32} className="spin-loader" />
                <div className="loading-text-group">
                  <span className="loading-title">Loading 3D Cow Model</span>
                  <span className="loading-subtitle">
                    Preparing high-resolution geometry...
                  </span>
                </div>
              </div>
            }
          >
            <Canvas
              camera={{ position: [2.6, 1.1, 2.7], fov: 36 }}
              dpr={[1, 2]}
              gl={{
                antialias: true,
                alpha: true,
                powerPreference: "high-performance",
              }}
            >
              {/* Natural, Calm Agricultural Lighting */}
              <ambientLight intensity={1.35} color="#F7F8F4" />

              {/* Soft Key Sunlight */}
              <directionalLight
                position={[5, 7, 5]}
                intensity={1.7}
                color="#FFFFFF"
              />

              {/* Soft Fill Light */}
              <directionalLight
                position={[-5, 3, -2]}
                intensity={0.8}
                color="#EAF2EC"
              />

              {/* Natural Rim / Back Light */}
              <directionalLight
                position={[0, 4, -5]}
                intensity={0.9}
                color="#F7F8F4"
              />

              {/* Soft Front Muzzle Light */}
              <pointLight
                position={[0, 1.2, 3]}
                intensity={0.5}
                color="#FFFFFF"
              />

              {/* The 3D Cow Model */}
              <CowModel currentAnim={selectedAnim} />

              {/* Soft Ground Contact Shadow */}
              <ContactShadows
                position={[0, -0.78, 0]}
                opacity={0.28}
                scale={6.5}
                blur={2.4}
                far={2.8}
                color="#24443A"
              />

              {/* Stationary by default Orbit Controls with smooth manual dragging */}
              <OrbitControls
                ref={controlsRef}
                target={[0, 0, 0]}
                enablePan={false}
                enableZoom={true}
                minDistance={1.8}
                maxDistance={5.8}
                autoRotate={false}
                enableDamping={true}
                dampingFactor={0.06}
                maxPolarAngle={Math.PI / 2 + 0.05}
                minPolarAngle={Math.PI / 6}
              />
            </Canvas>
          </Suspense>
        </ThreeErrorBoundary>
      </div>
    </div>
  );
}
