"use client";

import { useState, useRef, useEffect } from "react";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { OrbitControls, Sphere, Stars, Html } from "@react-three/drei";
import * as THREE from "three";
import { motion, AnimatePresence } from "framer-motion";

// ============================================================
// Живая сфера ATIG с реакцией на голос
// ============================================================
function IGSphere({ audioFrequency = 0 }: { audioFrequency: number }) {
  const meshRef = useRef<THREE.Mesh>(null);
  const materialRef = useRef<THREE.ShaderMaterial>(null);
  const pulse = 1 + audioFrequency * 0.5;

  useFrame(({ clock }) => {
    if (meshRef.current) {
      meshRef.current.scale.setScalar(pulse);
    }
    if (materialRef.current) {
      materialRef.current.uniforms.uTime.value = clock.getElapsedTime();
      materialRef.current.uniforms.uAudioIntensity.value = audioFrequency;
    }
  });

  return (
    <Sphere ref={meshRef} args={[1.2, 128, 128]}>
      <shaderMaterial
        ref={materialRef}
        uniforms={{
          uTime: { value: 0 },
          uAudioIntensity: { value: 0 },
        }}
        vertexShader={`
          varying vec2 vUv;
          void main() {
            vUv = uv;
            vec4 modelPosition = modelMatrix * vec4(position, 1.0);
            vec4 viewPosition = viewMatrix * modelPosition;
            vec4 projectedPosition = projectionMatrix * viewPosition;
            gl_PointSize = 3.0;
            gl_Position = projectedPosition;
          }
        `}
        fragmentShader={`
          uniform float uTime;
          uniform float uAudioIntensity;
          varying vec2 vUv;
          
          void main() {
            vec2 uv = vUv;
            float pulse = sin(uv.x * 20.0 + uTime) * cos(uv.y * 20.0 + uTime);
            float energy = pulse * 0.5 + uAudioIntensity * 0.8;
            
            vec3 color1 = vec3(0.2, 0.1, 0.6);
            vec3 color2 = vec3(0.8, 0.3, 0.9);
            vec3 color3 = vec3(1.0, 0.5, 0.2);
            
            vec3 finalColor = mix(color1, color2, uv.y);
            finalColor = mix(finalColor, color3, energy);
            
            float alpha = 0.85 + energy * 0.3;
            gl_FragColor = vec4(finalColor, alpha);
          }
        `}
        transparent
        side={THREE.DoubleSide}
      />
    </Sphere>
  );
}

// ============================================================
// Частицы
// ============================================================
function ParticleField() {
  const count = 2000;
  const positions = new Float32Array(count * 3);
  for (let i = 0; i < count; i++) {
    const radius = 1.8 + Math.random() * 0.5;
    const theta = Math.random() * Math.PI * 2;
    const phi = Math.acos(2 * Math.random() - 1);
    positions[i*3] = radius * Math.sin(phi) * Math.cos(theta);
    positions[i*3+1] = radius * Math.sin(phi) * Math.sin(theta);
    positions[i*3+2] = radius * Math.cos(phi);
  }

  return (
    <points>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" count={count} array={positions} itemSize={3} />
      </bufferGeometry>
      <pointsMaterial color="#a855f7" size={0.02} transparent opacity={0.6} blending={THREE.AdditiveBlending} />
    </points>
  );
}

// ============================================================
// Параллакс
// ============================================================
function ParallaxCamera() {
  const { camera } = useThree();
  const mouseX = useRef(0);
  const mouseY = useRef(0);

  useEffect(() => {
    const handleMove = (e: MouseEvent) => {
      mouseX.current = (e.clientX / window.innerWidth) * 2 - 1;
      mouseY.current = (e.clientY / window.innerHeight) * 2 - 1;
    };
    window.addEventListener("mousemove", handleMove);
    return () => window.removeEventListener("mousemove", handleMove);
  }, []);

  useFrame(() => {
    camera.position.x += (mouseX.current * 0.3 - camera.position.x) * 0.05;
    camera.position.y += (-mouseY.current * 0.2 - camera.position.y) * 0.05;
    camera.lookAt(0, 0, 0);
  });

  return null;
}

// ============================================================
// Главная страница
// ============================================================
export default function Home() {
  const [listening, setListening] = useState(false);
  const [audioFreq, setAudioFreq] = useState(0);
  const mediaStream = useRef<MediaStream | null>(null);
  const audioContext = useRef<AudioContext | null>(null);

  const startListening = async () => {
    if (listening) return;
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaStream.current = stream;
    audioContext.current = new AudioContext();
    const source = audioContext.current.createMediaStreamSource(stream);
    const analyser = audioContext.current.createAnalyser();
    analyser.fftSize = 256;
    source.connect(analyser);
    const dataArray = new Uint8Array(analyser.frequencyBinCount);
    const updateFreq = () => {
      if (!listening) return;
      analyser.getByteFrequencyData(dataArray);
      const avg = dataArray.reduce((a, b) => a + b, 0) / dataArray.length;
      setAudioFreq(avg / 255);
      requestAnimationFrame(updateFreq);
    };
    audioContext.current.resume();
    setListening(true);
    updateFreq();
  };

  const stopListening = () => {
    if (mediaStream.current) {
      mediaStream.current.getTracks().forEach(track => track.stop());
    }
    if (audioContext.current) {
      audioContext.current.close();
    }
    setListening(false);
    setAudioFreq(0);
  };

  return (
    <main className="relative w-full h-screen overflow-hidden bg-black">
      <Canvas
        camera={{ position: [0, 0, 3.5], fov: 45 }}
        gl={{ alpha: false, antialias: true, powerPreference: "high-performance" }}
        dpr={[1, 2]}
      >
        <color attach="background" args={["#010105"]} />
        <fog attach="fog" args={["#010105", 5, 12]} />
        <ambientLight intensity={0.2} />
        <pointLight position={[5, 5, 5]} intensity={0.5} />
        <Stars radius={100} depth={50} count={5000} factor={4} saturation={0} fade speed={0.5} />
        <IGSphere audioFrequency={audioFreq} />
        <ParticleField />
        <ParallaxCamera />
        <OrbitControls enableZoom={false} enablePan={false} rotateSpeed={0.5} />
      </Canvas>

      <div className="absolute bottom-12 left-0 right-0 flex justify-center z-20">
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={listening ? stopListening : startListening}
          className={`px-8 py-4 rounded-full font-bold text-lg backdrop-blur-xl border transition-all ${
            listening
              ? "bg-purple-600/30 border-purple-400 text-white shadow-[0_0_20px_rgba(168,85,247,0.5)]"
              : "bg-white/10 border-white/30 text-white hover:bg-white/20"
          }`}
        >
          {listening ? "🎙️ Слушаю... (нажми, чтобы выключить)" : "🎤 Говори со сферой"}
        </motion.button>
      </div>

      <div className="absolute top-8 left-8 z-20 text-white/60 text-sm font-mono">
        ATIG — живой интеллект
      </div>

      <AnimatePresence>
        {listening && audioFreq > 0.2 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="absolute top-32 left-0 right-0 text-center text-purple-300 font-light text-sm z-20 pointer-events-none"
          >
            ✦ сфера чувствует твой голос ✦
          </motion.div>
        )}
      </AnimatePresence>
    </main>
  );
}