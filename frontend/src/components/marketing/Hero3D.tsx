"use client";

import React, { useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Float, MeshTransmissionMaterial, Environment, ContactShadows } from '@react-three/drei';
import * as THREE from 'three';

// An organic looking cell
function Cell(props: any) {
  const meshRef = useRef<THREE.Mesh>(null);
  
  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.x = state.clock.elapsedTime * 0.2 + props.offset;
      meshRef.current.rotation.y = state.clock.elapsedTime * 0.3 + props.offset;
    }
  });

  return (
    <Float floatIntensity={2} rotationIntensity={1} speed={2}>
      <mesh ref={meshRef} {...props}>
        {/* IcosahedronGeometry with high detail creates a good base for organic shapes when combined with smooth shading */}
        <icosahedronGeometry args={[props.size || 1, 4]} />
        <MeshTransmissionMaterial
          backside
          backsideThickness={1}
          thickness={0.5}
          chromaticAberration={0.05}
          anisotropy={0.2}
          distortion={0.5}
          distortionScale={0.5}
          temporalDistortion={0.1}
          color={props.color || "#ffffff"}
          roughness={0.1}
        />
      </mesh>
    </Float>
  );
}

// A scanning laser effect
function ScannerLaser() {
  const laserRef = useRef<THREE.Mesh>(null);

  useFrame((state) => {
    if (laserRef.current) {
      // Move laser up and down to simulate scanning
      laserRef.current.position.y = Math.sin(state.clock.elapsedTime * 1.5) * 2.5;
    }
  });

  return (
    <mesh ref={laserRef} position={[0, 0, 1.5]}>
      <boxGeometry args={[10, 0.05, 0.05]} />
      <meshBasicMaterial color="#00ffff" transparent opacity={0.8} />
      <pointLight color="#00ffff" intensity={2} distance={5} />
    </mesh>
  );
}

export default function Hero3D() {
  return (
    <div className="w-full h-full min-h-[500px]">
      <Canvas camera={{ position: [0, 0, 8], fov: 45 }}>
        <color attach="background" args={['#050508']} />
        
        <ambientLight intensity={0.5} />
        <spotLight position={[10, 10, 10]} angle={0.15} penumbra={1} intensity={1} castShadow />
        
        {/* Center large cell */}
        <Cell position={[0, 0, 0]} size={1.8} color="#4f46e5" offset={0} />
        
        {/* Smaller floating cells */}
        <Cell position={[-3, 1.5, -2]} size={0.8} color="#9333ea" offset={1} />
        <Cell position={[2.5, -2, -1]} size={1.2} color="#06b6d4" offset={2} />
        <Cell position={[-2, -1.5, 1]} size={0.6} color="#3b82f6" offset={3} />
        <Cell position={[3, 2, -3]} size={1} color="#6366f1" offset={4} />

        <ScannerLaser />

        <ContactShadows position={[0, -3.5, 0]} opacity={0.4} scale={20} blur={2} far={4.5} color="#4f46e5" />
        <Environment preset="city" />
      </Canvas>
    </div>
  );
}
