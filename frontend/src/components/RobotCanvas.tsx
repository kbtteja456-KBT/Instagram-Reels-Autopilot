import React, { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';

interface RobotCanvasProps {
  className?: string;
}

export const RobotCanvas: React.FC<RobotCanvasProps> = ({ className = '' }) => {
  const mountRef = useRef<HTMLDivElement>(null);
  const [isHovered, setIsHovered] = useState(false);

  useEffect(() => {
    const container = mountRef.current;
    if (!container) return;

    const width = container.clientWidth || 240;
    const height = container.clientHeight || 260;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(40, width / height, 0.1, 100);
    camera.position.set(0, 0.3, 4.2);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    container.appendChild(renderer.domElement);

    // Lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.9);
    scene.add(ambientLight);

    const dirLight1 = new THREE.DirectionalLight(0xe1306c, 2.5); // Instagram rose
    dirLight1.position.set(2.5, 3, 2);
    scene.add(dirLight1);

    const dirLight2 = new THREE.DirectionalLight(0xf59e0b, 2.0); // Amber
    dirLight2.position.set(-2.5, 2, 2);
    scene.add(dirLight2);

    // Robot group
    const robotGroup = new THREE.Group();

    // Head
    const headGeo = new THREE.BoxGeometry(1.2, 1.0, 1.0);
    const headMat = new THREE.MeshStandardMaterial({
      color: 0x111827,
      metalness: 0.85,
      roughness: 0.2
    });
    const head = new THREE.Mesh(headGeo, headMat);
    head.position.y = 0.6;
    robotGroup.add(head);

    // Visor with glowing Instagram gradient feel
    const visorGeo = new THREE.BoxGeometry(0.9, 0.3, 0.15);
    const visorMat = new THREE.MeshBasicMaterial({ color: 0xe1306c });
    const visor = new THREE.Mesh(visorGeo, visorMat);
    visor.position.set(0, 0.65, 0.52);
    robotGroup.add(visor);

    // Torso
    const bodyGeo = new THREE.CylinderGeometry(0.7, 0.5, 1.2, 8);
    const bodyMat = new THREE.MeshStandardMaterial({
      color: 0x0f172a,
      metalness: 0.9,
      roughness: 0.3
    });
    const body = new THREE.Mesh(bodyGeo, bodyMat);
    body.position.y = -0.5;
    robotGroup.add(body);

    // Orbital Ring 1
    const ringGeo1 = new THREE.TorusGeometry(1.5, 0.02, 16, 100);
    const ringMat1 = new THREE.MeshBasicMaterial({ color: 0xf59e0b, transparent: true, opacity: 0.6 });
    const ring1 = new THREE.Mesh(ringGeo1, ringMat1);
    ring1.rotation.x = Math.PI / 3;
    robotGroup.add(ring1);

    // Orbital Ring 2
    const ringGeo2 = new THREE.TorusGeometry(1.7, 0.02, 16, 100);
    const ringMat2 = new THREE.MeshBasicMaterial({ color: 0xe1306c, transparent: true, opacity: 0.5 });
    const ring2 = new THREE.Mesh(ringGeo2, ringMat2);
    ring2.rotation.x = -Math.PI / 4;
    ring2.rotation.y = Math.PI / 6;
    robotGroup.add(ring2);

    // Floating particles
    const particleCount = 40;
    const pGeo = new THREE.BufferGeometry();
    const pPos = new Float32Array(particleCount * 3);
    for (let i = 0; i < particleCount * 3; i += 3) {
      pPos[i] = (Math.random() - 0.5) * 4;
      pPos[i + 1] = (Math.random() - 0.5) * 4;
      pPos[i + 2] = (Math.random() - 0.5) * 4;
    }
    pGeo.setAttribute('position', new THREE.BufferAttribute(pPos, 3));
    const pMat = new THREE.PointsMaterial({ color: 0xfcb045, size: 0.05 });
    const particles = new THREE.Points(pGeo, pMat);
    robotGroup.add(particles);

    scene.add(robotGroup);

    let frameId: number;
    let clock = new THREE.Clock();

    const animate = () => {
      frameId = requestAnimationFrame(animate);
      const elapsed = clock.getElapsedTime();

      // Floating bobbing motion
      robotGroup.position.y = Math.sin(elapsed * 1.5) * 0.1;
      robotGroup.rotation.y = Math.sin(elapsed * 0.5) * 0.2;

      ring1.rotation.z = elapsed * 0.8;
      ring2.rotation.z = -elapsed * 0.6;
      particles.rotation.y = elapsed * 0.1;

      renderer.render(scene, camera);
    };

    animate();

    const handleResize = () => {
      if (!container) return;
      const w = container.clientWidth || 240;
      const h = container.clientHeight || 260;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      cancelAnimationFrame(frameId);
      if (container && renderer.domElement) {
        container.removeChild(renderer.domElement);
      }
      renderer.dispose();
    };
  }, []);

  return (
    <div
      ref={mountRef}
      className={`relative w-full h-full flex items-center justify-center ${className}`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    />
  );
};
