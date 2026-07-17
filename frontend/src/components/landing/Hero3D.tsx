'use client';

import { useRef, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Float, Sphere, Instances, Instance, Environment } from '@react-three/drei';
import * as THREE from 'three';

const CellCluster = () => {
  const groupRef = useRef<THREE.Group>(null);
  const ringRef = useRef<THREE.Mesh>(null);
  const particlesCount = 40;
  
  const particles = useMemo(() => {
    const temp = [];
    for (let i = 0; i < particlesCount; i++) {
      const position = new THREE.Vector3(
        (Math.random() - 0.5) * 10,
        (Math.random() - 0.5) * 10,
        (Math.random() - 0.5) * 10
      );
      const scale = Math.random() * 0.5 + 0.2;
      const color = new THREE.Color().setHSL(
        0.6 + Math.random() * 0.1, // Blue-ish hues
        0.8,
        0.5 + Math.random() * 0.2
      );
      temp.push({ position, scale, color });
    }
    return temp;
  }, []);

  useFrame((state) => {
    if (groupRef.current) {
      groupRef.current.rotation.y = state.clock.elapsedTime * 0.05;
      groupRef.current.rotation.x = Math.sin(state.clock.elapsedTime * 0.1) * 0.1;
    }
    if (ringRef.current) {
      ringRef.current.position.y = Math.sin(state.clock.elapsedTime) * 4;
    }
  });

  return (
    <group ref={groupRef}>
      <Instances range={particlesCount}>
        <sphereGeometry args={[1, 32, 32]} />
        <meshPhysicalMaterial 
          transmission={0.9}
          opacity={1}
          metalness={0.1}
          roughness={0.1}
          ior={1.5}
          thickness={2}
          specularIntensity={1}
        />
        {particles.map((data, i) => (
          <Instance
            key={i}
            position={data.position}
            scale={data.scale}
            color={data.color}
          />
        ))}
      </Instances>
      {/* Scanning Laser Ring */}
      <mesh ref={ringRef} rotation={[-Math.PI / 2, 0, 0]}>
        <torusGeometry args={[6, 0.05, 16, 100]} />
        <meshBasicMaterial color="#0A66C2" transparent opacity={0.6} />
      </mesh>
    </group>
  );
};

export default function Hero3D() {
  return (
    <div className="absolute inset-0 z-0 opacity-40 pointer-events-none">
      <Canvas camera={{ position: [0, 0, 15], fov: 45 }}>
        <ambientLight intensity={0.5} />
        <spotLight position={[10, 10, 10]} angle={0.15} penumbra={1} intensity={2} color="#4285F4" />
        <pointLight position={[-10, -10, -10]} intensity={1} color="#EA4335" />
        <Float speed={1.5} rotationIntensity={1} floatIntensity={2}>
          <CellCluster />
        </Float>
      </Canvas>
    </div>
  );
}
