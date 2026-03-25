import { useEffect, useRef, useState } from "react";
import { Volume2, X } from "lucide-react";
import { Button } from "./ui/button";
import { Progress } from "./ui/progress";

interface VoicePreviewProps {
  voiceId: string | null;
  voiceName: string;
  onClose: () => void;
}

const SAMPLE_TEXTS: Record<string, string> = {
  xiaoyun: "大家好，我是晓云。欢迎收听今天的内容，希望我的声音能为您带来温暖和愉悦的体验。",
  yunyang: "各位观众朋友们好，我是云扬。接下来让我为您详细解说今天的重要新闻。",
  xiaochen: "嗨！我是晓辰！今天要给大家带来超级有趣的内容，快来一起看看吧！",
  yunxiao: "Hey大家好，我是云霄！今天给大家分享一些有意思的东西，记得点赞关注哦！",
  xiaomeng: "小朋友们好呀，我是晓梦老师。今天我们要学习的内容非常有趣，让我们一起开始吧！",
  yunhao: "晚上好，我是云浩。在这个宁静的夜晚，让我为您朗读一段优美的文字。"
};

export function VoicePreview({ voiceId, voiceName, onClose }: VoicePreviewProps) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [progress, setProgress] = useState(0);
  const audioContextRef = useRef<AudioContext | null>(null);

  useEffect(() => {
    if (voiceId) {
      playVoicePreview();
    }
    return () => {
      stopPreview();
    };
  }, [voiceId]);

  const playVoicePreview = () => {
    // 模拟音频播放
    setIsPlaying(true);
    setProgress(0);

    const duration = 3000; // 3秒模拟播放
    const interval = 50;
    let elapsed = 0;

    const timer = setInterval(() => {
      elapsed += interval;
      setProgress((elapsed / duration) * 100);

      if (elapsed >= duration) {
        clearInterval(timer);
        setIsPlaying(false);
        setProgress(100);
      }
    }, interval);

    // 清理函数
    return () => clearInterval(timer);
  };

  const stopPreview = () => {
    setIsPlaying(false);
    setProgress(0);
    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }
  };

  if (!voiceId) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-md flex items-center justify-center z-50 p-4">
      <div className="relative bg-white rounded-2xl shadow-[0_16px_48px_rgba(0,0,0,0.2)] border border-gray-200/60 max-w-md w-full p-6 space-y-4 overflow-hidden">
        {/* 装饰性光效 */}
        <div className="absolute top-0 right-0 w-72 h-72 bg-gradient-to-br from-cyan-300/20 to-transparent rounded-full blur-3xl"></div>
        {/* 顶部高光 */}
        <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/60 to-transparent"></div>
        
        <div className="relative flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="relative">
              <div className="absolute inset-0 bg-cyan-400/30 rounded-xl blur-md"></div>
              <div className="relative bg-gradient-to-br from-cyan-500 to-blue-600 p-2 rounded-xl shadow-md">
                <Volume2 className="w-5 h-5 text-white drop-shadow" />
              </div>
            </div>
            <h3 className="font-bold bg-gradient-to-r from-cyan-700 to-blue-700 bg-clip-text text-transparent">试听音色 - {voiceName}</h3>
          </div>
          <Button
            onClick={onClose}
            variant="ghost"
            size="sm"
            className="w-8 h-8 p-0 hover:bg-gray-100 text-gray-500"
          >
            <X className="w-4 h-4" />
          </Button>
        </div>

        <div className="relative bg-gradient-to-br from-cyan-50/90 to-blue-50/90 backdrop-blur rounded-xl p-4 space-y-3 border border-cyan-200/60 shadow-sm">
          <p className="text-sm text-gray-700 leading-relaxed font-medium">
            {SAMPLE_TEXTS[voiceId] || "这是一段示例音频，展示当前选择的音色效果。"}
          </p>

          <div className="space-y-2">
            <Progress value={progress} className="h-2" />
            <div className="flex items-center justify-between text-xs font-bold">
              <span className="text-cyan-700">{isPlaying ? "播放中..." : progress === 100 ? "播放完成" : "准备播放"}</span>
              <span className="text-purple-700">{Math.round(progress)}%</span>
            </div>
          </div>
        </div>

        <div className="relative flex gap-2">
          <Button
            onClick={playVoicePreview}
            className="flex-1 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-700 hover:to-blue-700 shadow-lg shadow-cyan-500/30 font-semibold"
            disabled={isPlaying}
          >
            {isPlaying ? "播放中..." : "重新播放"}
          </Button>
          <Button onClick={onClose} variant="outline" className="flex-1 border-gray-300 hover:bg-gray-50 font-semibold">
            关闭
          </Button>
        </div>
      </div>
    </div>
  );
}