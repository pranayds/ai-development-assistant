# Voice Chat Streamlit App with Docker Audio Support

This Streamlit application uses PyAudio for voice recording and supports running in Docker with access to the host's audio devices.

## Running the App with Audio Support in Docker

### Platform-Specific Setup

Each platform has its own script to run the application with the appropriate audio configuration:

```bash
# Linux
chmod +x run-linux.sh
./run-linux.sh

# macOS
chmod +x run-macos.sh
./run-macos.sh

# Windows (from Command Prompt or PowerShell)
run-windows.bat
```

### Manual Platform-Specific Setup

#### Linux:
```bash
# Ensure PulseAudio is running
pulseaudio --check || pulseaudio --start

# Run the container
docker compose --profile linux up
```

#### macOS:
```bash
# Install SoX if not already installed
brew install sox

# Run the SoX audio server and the container
./run-macos.sh

# The app will be available at http://localhost:8501
```

#### Windows:
```
# From Command Prompt or PowerShell
run-windows.bat
```

## Troubleshooting Audio in Docker

### Common Issues and Solutions

1. **No audio devices detected**:
   - Check if the host audio devices are working properly
   - Verify that the correct Docker flags are being used for your platform
   - For Linux, ensure PulseAudio is running: `pulseaudio --check || pulseaudio --start`
   - For macOS, ensure SoX is installed and running: `brew install sox`
   - For Windows, ensure Docker Desktop is using WSL2 backend
   - If still having issues, try running the container with `--privileged` flag manually:
     ```bash
     docker run --privileged --device /dev/snd:/dev/snd -v /run/user/$(id -u)/pulse:/run/pulse -e PULSE_SERVER=unix:/run/pulse/native your-image
     ```

2. **Permission errors**:
   - Ensure your user has permission to access audio devices
   - For Linux: `sudo usermod -a -G audio $USER` (requires logout/login)

3. **Audio quality issues**:
   - Adjust buffer size in `services/audio.py` if you experience dropouts
   - Increase `CHUNK` size for better stability (at the cost of latency)

### Debugging

The application includes enhanced logging for audio devices. Check the console output for:
- Environment detection information
- Available audio devices
- Selected input device
- Audio initialization status

## Technical Details

### Linux Audio

On Linux, we use two approaches:
1. **PulseAudio Socket Sharing**: Mounts the PulseAudio socket from the host into the container
2. **ALSA Device Mapping**: Maps `/dev/snd` devices from the host to the container

### macOS Audio

On macOS, we use:
1. **Simulated Audio Recording**: Creates a dummy audio file and provides a clear message to the user
2. **Standard Port Mapping**: Maps container port 8501 to host port 8501

The application will:
1. Detect that it's running on macOS and create a simulated audio file
2. Display a message to the user explaining the limitation
3. Allow the user to type their question instead of using voice input

**Note**: Full audio recording support on macOS is not possible due to the containerization. This is a fundamental limitation of Docker on macOS, as it runs in a VM that doesn't have direct access to host hardware. For real microphone access on macOS, you would need to run the application directly on the host without Docker.

### Windows Audio

On Windows, we use:
1. **WSL2 Backend**: Docker Desktop with WSL2 backend for audio support
2. **Device Mapping**: Maps `/dev/snd` devices from WSL2 to the container

## Limitations

- Audio latency may be increased when running in a container
- Some specialized audio hardware may not be properly recognized
- macOS has more limited audio support due to its security model
- Windows support requires Docker Desktop with WSL2 backend

## Security Considerations

This solution uses several Docker features that provide elevated privileges to the container:

- **Privileged Mode**: The `--privileged` flag gives the container full access to host devices
- **IPC Host**: The `--ipc=host` flag allows the container to use the host's inter-process communication namespace
- **SYS_ADMIN Capability**: Grants the container administrative capabilities

These settings are necessary for reliable audio access but should be used with caution in production environments. For production deployments, consider:

1. Using a dedicated audio service container that other containers can communicate with
2. Implementing proper authentication and authorization for audio access
3. Restricting the container's capabilities to only those absolutely necessary
