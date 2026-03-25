import { useEffect, useMemo, useState } from "react";
import { VideoUploader } from "./components/VideoUploader";
import { VideoPreview } from "./components/VideoPreview";
import { VoiceSelector } from "./components/VoiceSelector";
import { VoicePreview } from "./components/VoicePreview";
import { ScriptEditor } from "./components/ScriptEditor";
import { Button } from "./components/ui/button";
import { Switch } from "./components/ui/switch";
import { Input } from "./components/ui/input";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "./components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "./components/ui/select";
import { Label } from "./components/ui/label";
import { Film, Loader2, RefreshCcw, Sparkles } from "lucide-react";
import { toast, Toaster } from "sonner";

type VoiceOption = { id: string; name: string; description?: string; code?: string };

export default function App() {
  const [selectedVideo, setSelectedVideo] = useState<File | null>(null);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [selectedVoice, setSelectedVoice] = useState<string>("xiaoyun");
  const [previewVoice, setPreviewVoice] = useState<{ id: string; name: string } | null>(null);
  const [voices, setVoices] = useState<VoiceOption[]>([]);
  const [startTime, setStartTime] = useState<number>(0);
  const [endTime, setEndTime] = useState<number>(0);
  const [script, setScript] = useState<string>("");
  const [clipCount, setClipCount] = useState<string>("1");
  const [clipDialogOpen, setClipDialogOpen] = useState(false);
  const [enableVoiceover, setEnableVoiceover] = useState(true);
  const [voiceoverTopic, setVoiceoverTopic] = useState("");
  const [targetSeconds, setTargetSeconds] = useState("40");
  const [voiceToken, setVoiceToken] = useState("");
  const [loadingVoices, setLoadingVoices] = useState(false);
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    let active = true;
    const loadSettings = async () => {
      try {
        const resp = await fetch("/api/settings");
        const data = await resp.json();
        if (!active) return;
        if (data?.success && typeof data?.settings?.voiceToken === "string") {
          const cachedToken = String(data.settings.voiceToken || "").trim();
          setVoiceToken(cachedToken);
          if (cachedToken) {
            setLoadingVoices(true);
            try {
              const voicesResp = await fetch("/api/voices", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ token: cachedToken, refresh: true }),
              });
              const voicesData = await voicesResp.json();
              if (voicesData?.success) {
                const parsed: VoiceOption[] = (Array.isArray(voicesData.voices) ? voicesData.voices : []).map(
                  (item: { value?: string; label?: string; name?: string; code?: string }) => {
                    const code = String(item.code || item.value || "");
                    const name = String(item.name || item.label || code || "Unknown Voice");
                    return {
                      id: code,
                      name,
                      code,
                      description: code,
                    };
                  }
                );
                if (active) {
                  setVoices(parsed);
                  if (parsed.length > 0) {
                    setSelectedVoice(parsed[0].id);
                  }
                }
              }
            } catch {
              // Ignore auto-fetch failures on initial load.
            } finally {
              if (active) {
                setLoadingVoices(false);
              }
            }
          }
        }
      } catch {
        // Ignore loading errors.
      }
    };
    void loadSettings();
    return () => {
      active = false;
    };
  }, []);

  const persistSettings = async (tokenOverride?: string) => {
    const tokenToSave = (tokenOverride ?? voiceToken).trim();
    try {
      await fetch("/api/settings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ voiceToken: tokenToSave }),
      });
    } catch {
      // Ignore save errors.
    }
  };

  const voiceNameMap = useMemo(() => {
    const map: Record<string, string> = {
      xiaoyun: "晓云",
      yunyang: "云扬",
      xiaochen: "晓辰",
      yunxiao: "云霄",
      xiaomeng: "晓梦",
      yunhao: "云浩",
    };
    voices.forEach((item) => {
      map[item.id] = item.name;
    });
    return map;
  }, [voices]);

  const handleTimeRangeChange = (start: number, end: number) => {
    setStartTime(start);
    setEndTime(end);
  };

  const handleVoicePreview = (voiceId: string) => {
    setPreviewVoice({ id: voiceId, name: voiceNameMap[voiceId] || voiceId });
  };

  const handleOpenClipDialog = () => {
    if (!selectedVideo) {
      toast.error("请先选择视频文件");
      return;
    }
    setClipDialogOpen(true);
  };

  const executeGenerateFlow = async () => {
    const hasScript = Boolean(script.trim());
    const hasTopic = Boolean(voiceoverTopic.trim());
    const secs = Number.parseInt(targetSeconds, 10);
    if (!hasScript && !hasTopic && (!Number.isFinite(secs) || secs <= 0)) {
      toast.error("请先输入目标视频秒数。");
      return;
    }
    setClipDialogOpen(false);
    await handleExport();
  };

  const handleStartClip = async () => {
    if (!script.trim() && !voiceoverTopic.trim() && !(Number.parseInt(targetSeconds, 10) > 0)) {
      toast.error("请输入文案主题");
      return;
    }

    setClipDialogOpen(false);
    if (enableVoiceover && !script.trim() && voiceoverTopic.trim()) {
      try {
        const generated = await generateScriptFromApi(voiceoverTopic.trim());
        setScript(generated);
      } catch (error) {
        toast.error(error instanceof Error ? error.message : "生成口播文案失败");
        return;
      }
    }
    toast.success(`已配置完成，准备导出 ${clipCount} 个视频`);
  };

  async function generateScriptFromApi(requirement: string): Promise<string> {
    const resp = await fetch("/api/script", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ requirement, seconds: 40 }),
    });
    const data = await resp.json();
    if (!data.success) {
      throw new Error(data.message || "文案生成失败");
    }
    return String(data.script || "");
  }

  const fetchVoices = async () => {
    if (!voiceToken.trim()) {
      toast.error("请先填写 Token");
      return;
    }
    await persistSettings(voiceToken);
    setLoadingVoices(true);
    try {
      const resp = await fetch("/api/voices", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token: voiceToken, refresh: true }),
      });
      const data = await resp.json();
      if (!data.success) {
        throw new Error(data.message || "音色拉取失败");
      }
      const parsed: VoiceOption[] = (Array.isArray(data.voices) ? data.voices : []).map(
        (item: { value?: string; label?: string; name?: string; code?: string }) => {
          const code = String(item.code || item.value || "");
          const name = String(item.name || item.label || code || "未命名音色");
          return {
            id: code,
            name,
            code,
            description: code,
          };
        }
      );
      setVoices(parsed);
      if (parsed.length > 0) {
        setSelectedVoice(parsed[0].id);
      }
      toast.success(`已拉取 ${parsed.length} 个音色`);
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "音色拉取失败");
    } finally {
      setLoadingVoices(false);
    }
  };

  const handleExport = async () => {
    if (selectedFiles.length === 0) {
      toast.error("请先选择素材目录");
      return;
    }
    if (enableVoiceover && !script.trim() && !voiceoverTopic.trim()) {
      toast.error("请先输入或生成口播文案");
      return;
    }

    setExporting(true);
    try {
      let scriptToUse = script.trim();
      if (!scriptToUse && voiceoverTopic.trim()) {
        const generated = await generateScriptFromApi(voiceoverTopic.trim());
        scriptToUse = generated.trim();
        setScript(scriptToUse);
      }
      const useVoiceover = Boolean(scriptToUse);
      const targetDuration = !useVoiceover ? Number.parseInt(targetSeconds, 10) : undefined;

      const uploadForm = new FormData();
      selectedFiles.forEach((file) => uploadForm.append("files", file));
      const uploadResp = await fetch("/api/upload-clips", { method: "POST", body: uploadForm });
      const uploadData = await uploadResp.json();
      if (!uploadData.success) {
        throw new Error(uploadData.message || "素材上传失败");
      }
      const clips: string[] = Array.isArray(uploadData.clips) ? uploadData.clips : [];
      const count = Math.max(1, Number.parseInt(clipCount, 10) || 1);

      for (let i = 0; i < count; i += 1) {
        const outputName = count === 1 ? "mixed_output.mp4" : `mixed_output_${i + 1}.mp4`;
        const mixResp = await fetch("/api/mix", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            clips,
            outputName,
            transition: "fade",
            transitionDuration: 1.0,
            randomizeOrder: true,
            overlayText: "",
            targetDuration,
            voiceover: {
              enabled: useVoiceover,
              text: scriptToUse,
              token: voiceToken,
              speaker: selectedVoice,
              subtitlesEnabled: true,
              subtitleFontsize: 40,
              subtitleFontcolor: "white",
              matchVideoDuration: true,
            },
          }),
        });
        const mixData = await mixResp.json();
        if (!mixData.success) {
          throw new Error(mixData.message || `第 ${i + 1} 条导出失败`);
        }
        if (mixData.downloadUrl) {
          window.open(mixData.downloadUrl, "_blank");
        }
      }

      toast.success(`导出完成，共 ${count} 条视频`);
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "导出失败");
    } finally {
      setExporting(false);
    }
  };

  const voiceSelectorVoices = voices.length
    ? voices
    : [
        { id: "xiaoyun", name: "晓云", description: "默认温柔女声" },
        { id: "yunyang", name: "云扬", description: "默认沉稳男声" },
      ];

  return (
    <div className="relative min-h-screen overflow-hidden bg-gradient-to-br from-slate-100 via-gray-50 to-slate-100">
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="absolute left-1/4 top-0 h-[500px] w-[500px] rounded-full bg-gradient-to-br from-indigo-200/30 to-purple-200/30 blur-3xl" />
        <div className="absolute bottom-0 right-1/4 h-[500px] w-[500px] rounded-full bg-gradient-to-br from-purple-200/30 to-pink-200/30 blur-3xl" />
        <div className="absolute left-1/2 top-1/2 h-[500px] w-[500px] rounded-full bg-gradient-to-br from-cyan-200/20 to-blue-200/20 blur-3xl" />
      </div>
      <div className="pointer-events-none absolute inset-0 bg-[linear-gradient(to_right,#00000008_1px,transparent_1px),linear-gradient(to_bottom,#00000008_1px,transparent_1px)] bg-[size:2rem_2rem]" />

      <Toaster position="top-center" />

      <header className="relative border-b border-gray-200/60 bg-white/70 shadow-[0_2px_16px_rgba(0,0,0,0.06)] backdrop-blur-2xl">
        <div className="mx-auto max-w-7xl px-6 py-5">
          <div className="flex items-center gap-4">
            <div className="relative">
              <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-600 opacity-40 blur-xl" />
              <div className="relative rounded-2xl bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 p-3 shadow-[0_8px_16px_rgba(99,102,241,0.3)]">
                <Film className="h-7 w-7 text-white drop-shadow-lg" />
              </div>
            </div>
            <div>
              <h1 className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 bg-clip-text text-3xl font-bold text-transparent drop-shadow-sm">
                AI 视频剪辑工作台
              </h1>
              <p className="mt-0.5 text-sm font-medium text-gray-500">智能剪辑 · 语音合成 · 一键生成</p>
            </div>
          </div>
        </div>
      </header>

      <main className="relative mx-auto max-w-7xl px-6 py-6">
        <div className="grid grid-cols-1 gap-5 lg:grid-cols-3">
          <div className="space-y-5 lg:col-span-2">
            <div className="relative overflow-hidden rounded-2xl border border-gray-200/60 bg-white/85 p-6 shadow-[0_8px_32px_rgba(0,0,0,0.08)] backdrop-blur-2xl">
              <div className="absolute right-0 top-0 h-72 w-72 rounded-full bg-gradient-to-br from-indigo-200/20 to-transparent blur-3xl" />
              <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/60 to-transparent" />

              <div className="relative grid grid-cols-1 gap-6 lg:grid-cols-2 lg:items-stretch">
                <div className="flex min-h-0 flex-col space-y-4">
                  <div className="flex items-center gap-2.5">
                    <div className="h-7 w-1 rounded-full bg-gradient-to-b from-indigo-500 via-purple-500 to-purple-600 shadow-lg shadow-indigo-500/40" />
                    <h2 className="bg-gradient-to-r from-indigo-700 to-purple-700 bg-clip-text text-lg font-bold text-transparent">视频文件</h2>
                  </div>
                  <VideoUploader onVideoSelect={setSelectedVideo} onFilesSelect={setSelectedFiles} selectedVideo={selectedVideo} />
                  <div className="flex min-h-0 flex-1 flex-col overflow-hidden rounded-xl border border-indigo-200/70 bg-gradient-to-br from-indigo-50/70 to-purple-50/70 p-3.5 shadow-inner">
                    <div className="mb-2 flex items-center justify-between">
                      <p className="text-sm font-bold text-indigo-700">视频列表</p>
                      <span className="rounded-full bg-white/90 px-2 py-0.5 text-xs font-semibold text-indigo-600">{selectedFiles.length} 个</span>
                    </div>
                    <div className="h-[150px] space-y-2 overflow-x-hidden overflow-y-auto pr-1 scrollbar-thin scrollbar-thumb-indigo-300 scrollbar-track-transparent">
                      {selectedFiles.length === 0 ? (
                        <div className="rounded-lg border border-dashed border-indigo-300/80 bg-white/70 p-3 text-center text-xs text-indigo-600">
                          选择素材目录后，这里会显示所有视频文件
                        </div>
                      ) : (
                        selectedFiles.map((file, index) => (
                          <div
                            key={`${file.name}_${index}`}
                            className={`flex min-w-0 items-center justify-between rounded-lg border px-2.5 py-2 text-xs ${
                              index === 0
                                ? "border-indigo-300 bg-indigo-100/80 text-indigo-800"
                                : "border-indigo-100 bg-white/80 text-gray-700"
                            }`}
                          >
                            <span className="mr-2 min-w-0 flex-1 truncate">{file.name}</span>
                            <span className="shrink-0 text-[11px] text-indigo-600">{Math.max(1, Math.round(file.size / 1024 / 1024))}MB</span>
                          </div>
                        ))
                      )}
                    </div>
                  </div>
                </div>

                <div className="min-h-0 space-y-4">
                  <ScriptEditor script={script} onScriptChange={setScript} onGenerateScript={generateScriptFromApi} />
                </div>
              </div>
            </div>

            <div className="relative overflow-hidden rounded-2xl border border-gray-200/60 bg-white/85 p-6 shadow-[0_8px_32px_rgba(0,0,0,0.08)] backdrop-blur-2xl">
              <div className="absolute bottom-0 left-0 h-72 w-72 rounded-full bg-gradient-to-tr from-purple-200/20 to-transparent blur-3xl" />
              <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/60 to-transparent" />
              <div className="relative mb-4 flex items-center gap-2.5">
                <div className="h-7 w-1 rounded-full bg-gradient-to-b from-purple-500 via-pink-500 to-pink-600 shadow-lg shadow-purple-500/40" />
                <h2 className="bg-gradient-to-r from-purple-700 to-pink-700 bg-clip-text text-lg font-bold text-transparent">视频预览与剪辑</h2>
              </div>
              <div className="relative">
                <VideoPreview videoFile={selectedVideo} startTime={startTime} endTime={endTime} onTimeRangeChange={handleTimeRangeChange} onStartClip={handleOpenClipDialog} />
              </div>
            </div>
          </div>

          <div className="space-y-5">
            <div className="relative overflow-hidden rounded-2xl border border-gray-200/60 bg-white/85 p-6 shadow-[0_8px_32px_rgba(0,0,0,0.08)] backdrop-blur-2xl">
              <div className="relative z-20 mb-3 space-y-2">
                <Label className="text-sm font-semibold text-gray-700">语音 Token</Label>
                <div className="flex gap-2">
                  <Input
                    value={voiceToken}
                    onChange={(e) => setVoiceToken(e.target.value)}
                    onBlur={() => {
                      void persistSettings();
                    }}
                    placeholder="Bearer sk-xxxx"
                    className="border-cyan-200 bg-cyan-50/40"
                  />
                  <Button onClick={fetchVoices} disabled={loadingVoices} variant="outline" className="border-cyan-300 text-cyan-700">
                    {loadingVoices ? <Loader2 className="h-4 w-4 animate-spin" /> : <RefreshCcw className="h-4 w-4" />}
                  </Button>
                </div>
              </div>

              <div className="pointer-events-none absolute left-0 top-0 h-56 w-56 rounded-full bg-gradient-to-br from-cyan-200/20 to-transparent blur-3xl" />
              <div className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/60 to-transparent" />
              <div className="relative z-10">
                <VoiceSelector selectedVoice={selectedVoice} onVoiceChange={setSelectedVoice} onPreview={handleVoicePreview} voices={voiceSelectorVoices} />
              </div>
            </div>

            <div className="relative h-px bg-gradient-to-r from-transparent via-gray-300/50 to-transparent shadow-sm" />

            <div className="relative overflow-hidden rounded-2xl border border-gray-200/60 bg-white/85 p-6 shadow-[0_8px_32px_rgba(0,0,0,0.08)] backdrop-blur-2xl">
              <div className="absolute bottom-0 right-0 h-56 w-56 rounded-full bg-gradient-to-tl from-emerald-200/20 to-transparent blur-3xl" />
              <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/60 to-transparent" />
              <div className="relative mb-4 flex items-center gap-2.5">
                <div className="h-7 w-1 rounded-full bg-gradient-to-b from-emerald-500 via-teal-500 to-teal-600 shadow-lg shadow-emerald-500/40" />
                <h3 className="bg-gradient-to-r from-emerald-700 to-teal-700 bg-clip-text font-bold text-transparent">生成设置</h3>
              </div>
              <div className="relative space-y-2.5 text-sm">
                <div className="flex items-center justify-between rounded-xl border border-indigo-100/80 bg-gradient-to-r from-indigo-50/90 to-purple-50/90 p-3.5 shadow-sm backdrop-blur">
                  <span className="font-semibold text-gray-600">素材数量</span>
                  <span className="font-bold text-indigo-700">{selectedFiles.length} 个</span>
                </div>
                <div className="flex items-center justify-between rounded-xl border border-purple-100/80 bg-gradient-to-r from-purple-50/90 to-pink-50/90 p-3.5 shadow-sm backdrop-blur">
                  <span className="font-semibold text-gray-600">剪辑时长</span>
                  <span className="font-bold text-purple-700">{(endTime - startTime).toFixed(1)} 秒</span>
                </div>
                <div className="flex items-center justify-between rounded-xl border border-pink-100/80 bg-gradient-to-r from-pink-50/90 to-rose-50/90 p-3.5 shadow-sm backdrop-blur">
                  <span className="font-semibold text-gray-600">配音音色</span>
                  <span className="font-bold text-pink-700">{voiceNameMap[selectedVoice] || selectedVoice}</span>
                </div>
                <div className="flex items-center justify-between rounded-xl border border-emerald-100/80 bg-gradient-to-r from-emerald-50/90 to-teal-50/90 p-3.5 shadow-sm backdrop-blur">
                  <span className="font-semibold text-gray-600">文案字数</span>
                  <span className="font-bold text-emerald-700">{script.length} 字</span>
                </div>
              </div>

              <div className="relative mt-4 space-y-2">
                <Label className="text-sm font-semibold text-gray-700">剪辑数量</Label>
                <Select value={clipCount} onValueChange={setClipCount}>
                  <SelectTrigger className="border-blue-200 bg-gradient-to-r from-blue-50/50 to-cyan-50/50 font-semibold shadow-sm focus:border-blue-500 focus:ring-blue-500">
                    <SelectValue placeholder="选择数量" />
                  </SelectTrigger>
                  <SelectContent>
                    {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((num) => (
                      <SelectItem key={num} value={num.toString()}>
                        生成 {num} 个视频
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="relative mt-4 flex items-center justify-between rounded-xl border border-purple-200/60 bg-gradient-to-r from-purple-50/80 to-pink-50/80 p-3 backdrop-blur">
                <div className="space-y-0.5">
                  <Label htmlFor="enable-voiceover-main" className="cursor-pointer text-sm font-bold text-gray-800">
                    启用口播
                  </Label>
                  <p className="text-xs text-gray-600">开启后会合成语音并自动烧录字幕</p>
                </div>
                <Switch id="enable-voiceover-main" checked={enableVoiceover} onCheckedChange={setEnableVoiceover} />
              </div>

              <div className="relative mt-5">
                <Button
                  onClick={handleOpenClipDialog}
                  className="w-full gap-2 border-0 bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 font-semibold text-white shadow-[0_8px_24px_rgba(99,102,241,0.4)] transition-all duration-300 hover:scale-[1.02] hover:from-indigo-700 hover:via-purple-700 hover:to-pink-700 hover:shadow-[0_12px_32px_rgba(99,102,241,0.5)]"
                  size="lg"
                  disabled={selectedFiles.length === 0 || exporting}
                >
                  {exporting ? <Loader2 className="h-5 w-5 animate-spin" /> : <Sparkles className="h-5 w-5" />}
                  {exporting ? "生成中..." : "生成"}
                </Button>
                <Button
                  onClick={handleOpenClipDialog}
                  className="hidden w-full gap-2 border-0 bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 font-semibold text-white shadow-[0_8px_24px_rgba(99,102,241,0.4)] transition-all duration-300 hover:scale-[1.02] hover:from-indigo-700 hover:via-purple-700 hover:to-pink-700 hover:shadow-[0_12px_32px_rgba(99,102,241,0.5)]"
                  size="lg"
                  disabled={selectedFiles.length === 0 || exporting}
                >
                  {exporting ? <Loader2 className="h-5 w-5 animate-spin" /> : <Sparkles className="h-5 w-5" />}
                  {exporting ? "导出中..." : `导出 ${clipCount} 个视频`}
                </Button>
              </div>
            </div>
          </div>
        </div>
      </main>

      {previewVoice && <VoicePreview voiceId={previewVoice.id} voiceName={previewVoice.name} onClose={() => setPreviewVoice(null)} />}

      <Dialog open={clipDialogOpen} onOpenChange={setClipDialogOpen}>
        <DialogContent className="max-w-md border-gray-200 bg-white shadow-2xl">
          <DialogHeader>
            <DialogTitle className="bg-gradient-to-r from-pink-600 to-rose-600 bg-clip-text text-xl font-bold text-transparent">剪辑配置</DialogTitle>
            <DialogDescription className="font-medium text-gray-600">配置视频剪辑参数，选择是否添加AI口播</DialogDescription>
          </DialogHeader>

          <div className="space-y-5 py-4">
            <div className="space-y-2">
              <Label className="text-sm font-semibold text-gray-700">剪辑数量</Label>
              <Select value={clipCount} onValueChange={setClipCount}>
                <SelectTrigger className="border-blue-200 bg-gradient-to-r from-blue-50/50 to-cyan-50/50 font-semibold shadow-sm focus:border-blue-500 focus:ring-blue-500">
                  <SelectValue placeholder="选择数量" />
                </SelectTrigger>
                <SelectContent>
                  {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((num) => (
                    <SelectItem key={num} value={num.toString()}>
                      生成 {num} 个视频
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="flex items-center justify-between rounded-xl border border-purple-200/60 bg-gradient-to-r from-purple-50/80 to-pink-50/80 p-4 backdrop-blur">
              <div className="space-y-0.5">
                <Label htmlFor="enable-voiceover" className="cursor-pointer text-sm font-bold text-gray-800">
                  添加AI口播
                </Label>
                <p className="text-xs text-gray-600">自动生成口播文案并配音</p>
              </div>
              <Switch
                id="enable-voiceover"
                checked={enableVoiceover}
                onCheckedChange={setEnableVoiceover}
                className="scale-125 data-[state=checked]:bg-gradient-to-r data-[state=checked]:from-purple-600 data-[state=checked]:to-pink-600 data-[state=unchecked]:bg-gray-300"
              />
            </div>

            {enableVoiceover && (
              <div className="animate-in slide-in-from-top-2 fade-in space-y-2 duration-300">
                <Label htmlFor="voiceover-topic" className="text-sm font-semibold text-gray-700">
                  文案主题
                </Label>
                <Input
                  id="voiceover-topic"
                  placeholder="例如：健康生活方式、科技产品评测"
                  value={voiceoverTopic}
                  onChange={(e) => setVoiceoverTopic(e.target.value)}
                  className="border-purple-200 bg-purple-50/50 font-medium shadow-sm focus:border-purple-500 focus:ring-purple-500"
                />
                <p className="text-xs font-medium text-purple-600">AI 将根据主题自动生成约 40 秒口播文案</p>
              </div>
            )}

            {!script.trim() && !voiceoverTopic.trim() && (
              <div className="space-y-2">
                <Label htmlFor="target-seconds" className="text-sm font-semibold text-gray-700">
                  目标视频秒数
                </Label>
                <Input
                  id="target-seconds"
                  type="number"
                  min={1}
                  value={targetSeconds}
                  onChange={(e) => setTargetSeconds(e.target.value)}
                  placeholder="例如 30"
                  className="border-purple-200 bg-purple-50/50 font-medium shadow-sm focus:border-purple-500 focus:ring-purple-500"
                />
                <p className="text-xs text-gray-600">无文案时按这个时长随机混剪素材。</p>
              </div>
            )}

            <div className="flex gap-2 pt-2">
              <Button onClick={executeGenerateFlow} className="flex-1 bg-gradient-to-r from-pink-600 to-rose-600 font-semibold shadow-lg shadow-pink-500/30 hover:from-pink-700 hover:to-rose-700">
                确认
              </Button>
              <Button variant="outline" onClick={() => setClipDialogOpen(false)} className="flex-1 border-gray-300 font-semibold hover:bg-gray-50">
                取消
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
