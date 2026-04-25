/* eslint-disable no-tabs */
import * as THREE from 'three';

export default {
  extensions: {
    derivatives: '#extension GL_OES_standard_derivatives : enable',
  },
  side: THREE.DoubleSide,
  uniforms: {
    time: { value: 0 },
    tCube: { value: 0 },
    mRefractionRatio: { value: 1.02 },
    mFresnelBias: { value: 0.1 },
    mFresnelScale: { value: 4.0 },
    mFresnelPower: { value: 2.0 },
    resolution: { value: new THREE.Vector2() },
  },
  // wireframe: true,
  // transparent: true,
  vertexShader: `
    uniform float time;
    varying vec2 vUv;
    varying vec3 vPosition;
    uniform vec2 pixels;
    float PI = 3.141592653589793238;

    varying vec3 vReflect;
    varying vec3 vRefract[3];
    varying float vReflectionFactor;

    uniform float mRefractionRatio;
    uniform float mFresnelBias ;
    uniform float mFresnelScale;
    uniform float mFresnelPower;

    void main() {

      vec4 mvPosition = modelViewMatrix * vec4( position, 1.0 );
      vec4 worldPosition = modelMatrix * vec4( position, 1.0 );

      vec3 worldNormal = normalize( mat3( modelMatrix[0].xyz, modelMatrix[1].xyz, modelMatrix[2].xyz ) * normal );

      vec3 I = worldPosition.xyz - cameraPosition;

      vReflect = reflect( I, worldNormal );
      vRefract[0] = refract( normalize( I ), worldNormal, mRefractionRatio );
      vRefract[1] = refract( normalize( I ), worldNormal, mRefractionRatio * 0.99 );
      vRefract[2] = refract( normalize( I ), worldNormal, mRefractionRatio * 0.98 );
      vReflectionFactor = mFresnelBias + mFresnelScale * pow( 1.0 + dot( normalize( I ), worldNormal ), mFresnelPower );

      gl_Position = projectionMatrix * mvPosition;
    }
  `,
  fragmentShader: `
    uniform samplerCube tCube;
    varying vec3 vPosition;

    varying vec3 vReflect;
    varying vec3 vRefract[3];
    varying float vReflectionFactor;

    void main() {

      vec4 reflectedColor = textureCube( tCube, vec3( -vReflect.x, vReflect.yz ) );
      vec4 refractedColor = vec4( 1.0 );

      refractedColor.r = textureCube( tCube, vec3( vRefract[0].x, vRefract[0].yz ) ).r;
      refractedColor.g = textureCube( tCube, vec3( vRefract[1].x, vRefract[1].yz ) ).g;
      refractedColor.b = textureCube( tCube, vec3( vRefract[2].x, vRefract[2].yz ) ).b;

      gl_FragColor = mix( refractedColor, reflectedColor, clamp( vReflectionFactor, 0.0, 1.0 ) );
    }
  `,
};
