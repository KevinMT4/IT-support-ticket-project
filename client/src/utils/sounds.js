const playBeep = (frequency, duration, volume = 0.3) => {
  try {
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();

    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);

    oscillator.frequency.value = frequency;
    oscillator.type = 'sine';

    gainNode.gain.setValueAtTime(volume, audioContext.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + duration);

    oscillator.start(audioContext.currentTime);
    oscillator.stop(audioContext.currentTime + duration);
  } catch (error) {
    console.warn('Error al reproducir sonido:', error);
  }
};

export const playNotificationSound = () => {
  playBeep(800, 0.1, 0.3);
  setTimeout(() => playBeep(1000, 0.1, 0.3), 100);
};

export const playSuccessSound = () => {
  playBeep(523.25, 0.1, 0.3);
  setTimeout(() => playBeep(659.25, 0.1, 0.3), 100);
  setTimeout(() => playBeep(783.99, 0.15, 0.3), 200);
};
