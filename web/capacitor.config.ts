import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'in.kabadiwalaconnect.collector',
  appName: 'Kabadiwala Connect',
  webDir: 'dist',
  
  android: {
    // Background color matching paper-50
    backgroundColor: '#F7F5EF',
    
    // WebView debugging only in debug builds (controlled via Gradle buildConfigField)
    webContentsDebuggingEnabled: false,
    
    // No logging in release
    loggingBehavior: 'none',
    
    // Build the web assets into the APK (no live server)
    path: 'android',
  },
  
  plugins: {
    SplashScreen: {
      launchShowDuration: 2000,
      launchAutoHide: true,
      backgroundColor: '#F7F5EF',
      androidSplashResourceName: 'splash',
      androidScaleType: 'CENTER_CROP',
      showSpinner: false,
    },
    StatusBar: {
      style: 'DARK',
      backgroundColor: '#0B3D2E',
    },
    Keyboard: {
      resize: 'native',
      resizeOnFullScreen: true,
    },
    Camera: {
      // Do not save to gallery by default (privacy)
      saveToGallery: false,
    },
    LocalNotifications: {
      smallIcon: 'ic_notification',
      iconColor: '#0B3D2E',
    },
  },
  
  server: {
    // In release: no server, assets bundled in APK
    // In demoLan builds: this can be overridden via env
    androidScheme: 'https',
    allowNavigation: [],
  },
};

export default config;
