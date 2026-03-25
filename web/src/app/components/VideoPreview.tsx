import { useEffect, useRef, useState } from "react";
import { Play, Pause, Volume2, VolumeX, Scissors, Clapperboard } from "lucide-react";
import { Button } from "./ui/button";
import { Slider } from "./ui/slider";

interface VideoPreviewProps {
  videoFile: File | null;
  startTime: number;
  endTime: number;
  onTimeRangeChange: (start: number, end: number) => void;
  onStartClip?: () => void;
}

export function VideoPreview({ videoFile, startTime, endTime, onTimeRangeChange }: VideoPreviewProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [isMuted, setIsMuted] = useState(false);
  const [videoUrl, setVideoUrl] = useState<string | null>(null);

  useEffect(() => {
    if (videoFile) {
      const url = URL.createObjectURL(videoFile);
      setVideoUrl(url);
      return () => URL.revokeObjectURL(url);
    }
  }, [videoFile]);

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    const handleTimeUpdate = () => setCurrentTime(video.currentTime);
    const handleLoadedMetadata = () => {
      setDuration(video.duration);
      onTimeRangeChange(0, video.duration);
    };
    const handleEnded = () => setIsPlaying(false);

    video.addEventListener('timeupdate', handleTimeUpdate);
    video.addEventListener('loadedmetadata', handleLoadedMetadata);
    video.addEventListener('ended', handleEnded);

    return () => {
      video.removeEventListener('timeupdate', handleTimeUpdate);
      video.removeEventListener('loadedmetadata', handleLoadedMetadata);
      video.removeEventListener('ended', handleEnded);
    };
  }, [onTimeRangeChange]);

  const togglePlay = () => {
    const video = videoRef.current;
    if (!video) return;

    if (isPlaying) {
      video.pause();
    } else {
      video.play();
    }
    setIsPlaying(!isPlaying);
  };

  const toggleMute = () => {
    const video = videoRef.current;
    if (!video) return;
    video.muted = !isMuted;
    setIsMuted(!isMuted);
  };

  const handleSeek = (value: number[]) => {
    const video = videoRef.current;
    if (!video) return;
    video.currentTime = value[0];
    setCurrentTime(value[0]);
  };

  const handleRangeChange = (values: number[]) => {
    onTimeRangeChange(values[0], values[1]);
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (!videoFile) {
    return (
      <div className="w-full aspect-video bg-gradient-to-br from-gray-100/90 to-gray-50/90 rounded-xl flex items-center justify-center border border-gray-200/60 backdrop-blur shadow-inner">
        <p className="text-gray-500 font-semibold">请先选择视频文件</p>
      </div>
    );
  }

  return (
    <div className="w-full space-y-4">
      <div className="relative rounded-xl overflow-hidden bg-black border border-gray-300/60 shadow-[0_8px_24px_rgba(0,0,0,0.15)]">
        <video
          ref={videoRef}
          src={videoUrl || undefined}
          className="w-full aspect-video"
        />
      </div>

      {/* 控制栏 */}
      <div className="space-y-3">
        <div className="flex items-center gap-3 p-4 bg-gradient-to-r from-indigo-50/90 to-purple-50/90 rounded-xl backdrop-blur border border-indigo-200/60 shadow-sm">
          <Button
            onClick={togglePlay}
            size="sm"
            variant="outline"
            className="w-11 h-11 p-0 border-indigo-300 text-indigo-700 hover:bg-indigo-100 shadow-sm font-semibold"
          >
            {isPlaying ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5" />}
          </Button>

          <div className="flex-1 flex items-center gap-3">
            <span className="text-sm text-indigo-700 w-12 font-bold">{formatTime(currentTime)}</span>
            <Slider
              value={[currentTime]}
              onValueChange={handleSeek}
              max={duration || 100}
              step={0.1}
              className="flex-1"
            />
            <span className="text-sm text-indigo-700 w-12 font-bold">{formatTime(duration)}</span>
          </div>

          <Button
            onClick={toggleMute}
            size="sm"
            variant="outline"
            className="w-11 h-11 p-0 border-purple-300 text-purple-700 hover:bg-purple-100 shadow-sm font-semibold"
          >
            {isMuted ? <VolumeX className="w-5 h-5" /> : <Volume2 className="w-5 h-5" />}
          </Button>
        </div>

        {/* 剪辑范围选择 */}
        <div className="bg-gradient-to-br from-purple-50/90 to-pink-50/90 backdrop-blur rounded-xl p-4 space-y-3 border border-purple-200/60 shadow-sm">
          <div className="flex items-center gap-2 text-sm font-bold text-gray-800">
            <div className="bg-gradient-to-br from-pink-500 to-rose-600 p-1.5 rounded-lg shadow-md">
              <Scissors className="w-4 h-4 text-white drop-shadow" />
            </div>
            <span>剪辑范围</span>
          </div>
          
          <div className="flex items-center gap-3">
            <span className="text-sm text-purple-700 w-12 font-bold">{formatTime(startTime)}</span>
            <Slider
              value={[startTime, endTime]}
              onValueChange={handleRangeChange}
              max={duration || 100}
              step={0.1}
              className="flex-1"
            />
            <span className="text-sm text-purple-700 w-12 font-bold">{formatTime(endTime)}</span>
          </div>
          <p className="text-xs text-gray-600 font-semibold">
            剪辑时长: <span className="text-purple-700 font-bold">{formatTime(endTime - startTime)}</span>
          </p>
        </div>
      </div>
    </div>
  );
}