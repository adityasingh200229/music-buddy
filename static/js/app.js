document.addEventListener('DOMContentLoaded', () => {
    const generateBtn = document.getElementById('generateBtn');
    const playBtn = document.getElementById('playBtn');
    const stopBtn = document.getElementById('stopBtn');
    const downloadBtn = document.getElementById('downloadBtn');
    const progressBar = document.getElementById('progressBar');
    const tempoSlider = document.getElementById('tempo');
    const tempoValue = document.getElementById('tempoValue');

    const synth = new Tone.PolySynth().toDestination();
    const chordSynth = new Tone.PolySynth().toDestination();
    chordSynth.volume.value = -8; // Slightly quieter than melody

    const drums = {
        kick: new Tone.MembraneSynth().toDestination(),
        snare: new Tone.NoiseSynth().toDestination(),
        hihat: new Tone.MetalSynth({
            frequency: 200,
            envelope: { attack: 0.001, decay: 0.1, release: 0.01 }
        }).toDestination()
    };

    let currentMelody = null;
    let isPlaying = false;
    let currentPlayback = null;

    tempoSlider.addEventListener('input', (e) => {
        tempoValue.textContent = `${e.target.value} BPM`;
    });

    const getParams = () => new URLSearchParams({
        key: document.getElementById('key').value,
        scale: document.getElementById('scale').value,
        tempo: document.getElementById('tempo').value,
        octave: document.getElementById('octave').value,
        enableChords: document.getElementById('enableChords').checked,
        enableDrums: document.getElementById('enableDrums').checked,
        genre: document.getElementById('genre').value
    });

    generateBtn.addEventListener('click', async () => {
        try {
            generateBtn.disabled = true;
            playBtn.disabled = true;
            stopBtn.disabled = true;
            downloadBtn.disabled = true;
            progressBar.style.width = '50%';

            const response = await fetch(`/generate?${getParams().toString()}`, {
                method: 'POST',
            });

            if (!response.ok) {
                throw new Error('Generation failed');
            }

            currentMelody = await response.blob();

            progressBar.style.width = '100%';
            playBtn.disabled = false;
            downloadBtn.disabled = false;
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to generate music');
        } finally {
            generateBtn.disabled = false;
            setTimeout(() => {
                progressBar.style.width = '0%';
            }, 1000);
        }
    });

    playBtn.addEventListener('click', () => {
        if (!isPlaying) {
            const key = document.getElementById('key').value;
            const scale = document.getElementById('scale').value;
            const tempo = parseInt(document.getElementById('tempo').value);
            const octave = parseInt(document.getElementById('octave').value);
            const enableChords = document.getElementById('enableChords').checked;
            const enableDrums = document.getElementById('enableDrums').checked;

            // Calculate note duration based on tempo
            const noteDuration = 60 / tempo;

            // Create preview melody
            const baseNote = key + octave;
            const interval = scale === 'major' ? 4 : 3;
            const notes = [
                baseNote,
                Tone.Frequency(baseNote).transpose(interval).toNote(),
                Tone.Frequency(baseNote).transpose(7).toNote(),
                baseNote
            ];

            // Set up the preview sequence
            const now = Tone.now();
            let time = now;

            // Play melody
            notes.forEach((note, i) => {
                synth.triggerAttackRelease(note, noteDuration, time);
                time += noteDuration;
            });

            // Play chords if enabled
            if (enableChords) {
                const chordRoot = Tone.Frequency(baseNote).transpose(-12).toNote(); // One octave down
                const chord = scale === 'major' 
                    ? [0, 4, 7] // Major triad
                    : [0, 3, 7]; // Minor triad

                chord.forEach(interval => {
                    chordSynth.triggerAttackRelease(
                        Tone.Frequency(chordRoot).transpose(interval).toNote(),
                        noteDuration * 4,
                        now
                    );
                });
            }

            // Play drums if enabled
            if (enableDrums) {
                const drumLoop = new Tone.Loop(time => {
                    drums.kick.triggerAttackRelease('C1', '8n', time);
                    drums.hihat.triggerAttackRelease('32n', time + noteDuration/2);
                    drums.snare.triggerAttackRelease('16n', time + noteDuration);
                    drums.hihat.triggerAttackRelease('32n', time + noteDuration*1.5);
                }, noteDuration * 2).start(now);

                currentPlayback = drumLoop;
            }

            isPlaying = true;
            playBtn.innerHTML = '<i class="bi bi-pause-circle"></i> Pause';
            stopBtn.disabled = false;
        } else {
            stopPlayback();
        }
    });

    const stopPlayback = () => {
        synth.releaseAll();
        chordSynth.releaseAll();
        if (currentPlayback) {
            currentPlayback.stop();
            currentPlayback.dispose();
            currentPlayback = null;
        }
        isPlaying = false;
        playBtn.innerHTML = '<i class="bi bi-play-circle"></i> Play';
        stopBtn.disabled = true;
    };

    stopBtn.addEventListener('click', stopPlayback);

    downloadBtn.addEventListener('click', () => {
        if (currentMelody) {
            const url = window.URL.createObjectURL(currentMelody);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'generated_music.mid';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        }
    });
});