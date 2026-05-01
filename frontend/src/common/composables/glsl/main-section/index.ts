import { ref } from 'vue';
import * as THREE from 'three';
// import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';

import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass.js';
import { ShaderPass } from 'three/examples/jsm/postprocessing/ShaderPass.js';

import { DotScreenShader } from './CustomShader';
import firstShader from './shader/firstShader';
import secondShader from './shader/secondShader';

interface additionOptions {
  useObserver?: boolean;
  defaultStart?: boolean;
  imageAspect?: number;
  mouseOffsetX?: number;
  mouseOffsetY?: number;
  mouseTolerance?: number;
  containerScrollTop?: number;
  MAX_CAMERA_ANGLE?: number;
}

export const useMainSectionShader = (
  container: HTMLElement | HTMLCanvasElement | null,
  canvas?: HTMLCanvasElement,
  {
    useObserver = true,
    defaultStart = true,
    mouseTolerance = 0.000012,
    containerScrollTop = 0,
    mouseOffsetX = -0.05,
    mouseOffsetY = 0,
    MAX_CAMERA_ANGLE = 30,
  }: additionOptions = {} as additionOptions,
) => {
  if (!container) {
    console.error('Canvas не указан');
    return {};
  }

  const scene = new THREE.Scene();

  /** @description Ширина и высота контейнера */
  const width = ref(container.offsetWidth);
  const height = ref(container.offsetHeight);

  /** @description Стандартные настройки рендеринга */
  const renderer = new THREE.WebGLRenderer({ canvas: canvas ?? container });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setClearColor(0xeeeeee, 1);
  renderer.physicallyCorrectLights = true;
  renderer.outputEncoding = THREE.sRGBEncoding;

  const time = ref<number>(0);
  const isPlaying = ref<boolean>(false);

  const composer = new EffectComposer(renderer);

  const camera = new THREE.PerspectiveCamera(
    70,
    width.value / height.value,
    0.001,
    1000,
  );

  const initPost = (): void => {
    composer.addPass(new RenderPass(scene, camera));

    const effect1 = new ShaderPass(DotScreenShader);
    effect1.uniforms.scale.value = 4;

    composer.addPass(effect1);
  };

  const observer = ref<ResizeObserver | null>(null);

  const resizeEvent = (): void => {
    width.value = container.offsetWidth;
    height.value = container.offsetHeight;

    renderer.setSize(width.value, height.value);
    composer.setSize(width.value, height.value);

    camera.aspect = width.value / height.value;
    camera.updateProjectionMatrix();
  };

  const onCanvasMouseMove = (evt: MouseEvent) => {
    const centerX = window.innerWidth * 0.5;
    const centerY = window.innerHeight * 0.5;

    const newX = (evt.clientX - centerX) * mouseTolerance;
    const newY = (evt.clientY - centerY) * mouseTolerance;

    camera.position.x = Math.max(-MAX_CAMERA_ANGLE, Math.min(MAX_CAMERA_ANGLE, newX));
    camera.position.y = Math.max(-MAX_CAMERA_ANGLE, Math.min(MAX_CAMERA_ANGLE, newY));
  };

  const setupResize = (): void => {
    if (useObserver) {
      observer.value = new ResizeObserver(() => resizeEvent());
      observer.value.observe(container);
      return;
    }
    window.addEventListener('resize', resizeEvent);
  };

  /**
   * ------------------------------------------------
   * @description Добавление элементов на сцену
   * ------------------------------------------------
   */
  const cubeRenderTarget = new THREE.WebGLCubeRenderTarget(256, {
    format: THREE.RGBAFormat,
    generateMipmaps: true,
    minFilter: THREE.LinearMipMapLinearFilter,
    encoding: THREE.sRGBEncoding,
  });

  const cubeCamera = new THREE.CubeCamera(0.6, 100, cubeRenderTarget);

  const material = new THREE.ShaderMaterial(firstShader);

  const geometry = new THREE.SphereGeometry(1.5, 32, 32);
  const plane = new THREE.Mesh(geometry, material);

  scene.add(plane);

  const mat = new THREE.ShaderMaterial(secondShader);

  const smallSphere = new THREE.Mesh(new THREE.SphereGeometry(0.7, 64, 64), mat);
  smallSphere.position.set(mouseOffsetX, mouseOffsetY, camera.position.z - 1.5);
  scene.add(smallSphere);
  /** ------------------------------------------------ */

  const onScroll = (scrollTop:number = containerScrollTop?.value ?? 0) => {
    const screenHeight = window.innerHeight;
    const t = Math.min(scrollTop / screenHeight, 1) * 0.8;
    smallSphere.position.y = (1 - t) * 0;
    smallSphere.position.y = THREE.MathUtils.lerp(0, 5, t);

    smallSphere.visible = t < 1;
  };

  /** @description Метод рендеринга */
  const render = (): void => {
    if (!isPlaying.value) return;
    time.value += 0.004;

    smallSphere.visible = false;
    cubeCamera.update(renderer, scene);

    smallSphere.visible = true;
    mat.uniforms.tCube.value = cubeRenderTarget.texture;
    material.uniforms.time.value = time.value;

    onScroll();

    requestAnimationFrame(render);
    composer.render(scene, camera);
  };

  const startDraw = (): void => {
    if (isPlaying.value) return;
    isPlaying.value = true;
    render();
  };

  const stopDraw = (): void => {
    isPlaying.value = false;
  };

  /**
   * @description Запускает все стартовые методы.
   */
  const startBaseMethods = (): void => {
    initPost();
    resizeEvent();
    render();
    document.addEventListener('mousemove', onCanvasMouseMove);
    setupResize();
  };

  const eliminateEvents = (): void => {
    if (observer.value) {
      observer.value.disconnect();
      observer.value = null;
    }
    window.removeEventListener('resize', resizeEvent);
    document.removeEventListener('mousemove', onCanvasMouseMove);
  };

  if (defaultStart) startBaseMethods();

  return {
    renderer,
    scene,
    camera,
    startDraw,
    stopDraw,
    time,
    width,
    onScroll,
    height,
    eliminateEvents,
  };
};

export default useMainSectionShader;
