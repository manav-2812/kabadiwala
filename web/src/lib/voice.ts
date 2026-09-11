export function speakText(text: string, lang: string = 'hi') {
  if (typeof window === 'undefined' || !('speechSynthesis' in window)) {
    return;
  }

  try {
    window.speechSynthesis.cancel(); // Stop any pending utterances
    const utterance = new SpeechSynthesisUtterance(text);
    
    // Map lang to BCP 47
    if (lang === 'mr') {
      utterance.lang = 'mr-IN';
    } else if (lang === 'hi') {
      utterance.lang = 'hi-IN';
    } else if (lang === 'pa') {
      utterance.lang = 'pa-IN';
    } else {
      utterance.lang = 'en-IN';
    }

    utterance.rate = 0.95;
    utterance.pitch = 1.0;
    window.speechSynthesis.speak(utterance);
  } catch (err) {
    console.warn('Speech synthesis failed silently:', err);
  }
}

export const speak = speakText;



export function startVoiceRecognition(
  onResult: (text: string) => void,
  onError?: (err: any) => void,
  lang: string = 'hi'
): () => void {
  const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
  if (!SpeechRecognition) {
    if (onError) onError(new Error('Speech recognition not supported in this browser'));
    return () => {};
  }

  try {
    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = lang === 'mr' ? 'mr-IN' : (lang === 'hi' ? 'hi-IN' : (lang === 'pa' ? 'pa-IN' : 'en-IN'));

    recognition.onresult = (event: any) => {
      if (event.results && event.results[0] && event.results[0][0]) {
        const transcript = event.results[0][0].transcript;
        onResult(transcript);
      }
    };

    recognition.onerror = (event: any) => {
      if (onError) onError(event);
    };

    recognition.start();
    return () => {
      try {
        recognition.stop();
      } catch {}
    };
  } catch (err) {
    if (onError) onError(err);
    return () => {};
  }
}
