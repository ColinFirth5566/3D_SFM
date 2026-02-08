declare module '@mkkellogg/gaussian-splats-3d' {
  import * as THREE from 'three';

  export enum WebXRMode {
    None = 0,
    VR = 1,
    AR = 2,
  }

  export enum RenderMode {
    Always = 0,
    OnChange = 1,
    Never = 2,
  }

  export enum SceneRevealMode {
    Default = 0,
    Gradual = 1,
    Instant = 2,
  }

  export interface ViewerOptions {
    scene?: THREE.Scene;
    camera?: THREE.Camera;
    renderer?: THREE.WebGLRenderer;
    selfDrivenMode?: boolean;
    useBuiltInControls?: boolean;
    ignoreDevicePixelRatio?: boolean;
    gpuAcceleratedSort?: boolean;
    sharedMemoryForWorkers?: boolean;
    integerBasedSort?: boolean;
    dynamicScene?: boolean;
    webXRMode?: WebXRMode;
    renderMode?: RenderMode;
    sceneRevealMode?: SceneRevealMode;
  }

  export interface SplatSceneOptions {
    splatAlphaRemovalThreshold?: number;
    showLoadingUI?: boolean;
    progressiveLoad?: boolean;
    position?: number[];
    rotation?: number[];
    scale?: number[];
    onProgress?: (percent: number) => void;
  }

  export class Viewer {
    constructor(options?: ViewerOptions);
    addSplatScene(url: string, options?: SplatSceneOptions): Promise<void>;
    update(): void;
    render(): void;
    dispose(): void;
  }
}
