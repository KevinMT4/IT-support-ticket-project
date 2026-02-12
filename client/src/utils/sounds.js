const playAudio = (fileName) => {
  try {
    const audio = new Audio(`/sounds/${fileName}`);
    audio.volume = 10;
    audio.play().catch(error => {
      console.warn(`No se pudo reproducir ${fileName}:`, error);
    });
  } catch (error) {
    console.warn(`Error al cargar audio ${fileName}:`, error);
  }
};

export const playNotificationSound = () => {
  playAudio('notification.mp3');
};

export const playSuccessSound = () => {
  playAudio('success.mp3');
};
