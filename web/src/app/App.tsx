import { useEffect, useMemo, useState } from "react";
import { VideoUploader } from "./components/VideoUploader";
import { FancyTextShowcase, type FancyTemplateId } from "./components/FancyTextShowcase";
import { PopupTemplateShowcase, type PopupTemplateId } from "./components/PopupTemplateShowcase";
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
import { BUILTIN_MANDARIN_VOICES, type VoiceCatalogItem } from "./voiceCatalog";

type VoiceOption = VoiceCatalogItem & { code?: string };
const DEFAULT_ACCESS_TOKEN = "nAblyxkQTcVaeBu4M0rKaphRuwkdlbOV";

export default function App() {
  const [selectedVideo, setSelectedVideo] = useState<File | null>(null);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [selectedBgmFiles, setSelectedBgmFiles] = useState<File[]>([]);
  const [bgmFolderName, setBgmFolderName] = useState<string>("");
  const [selectedVoice, setSelectedVoice] = useState<string>("BV700_V2_streaming");
  const [selectedEmotion, setSelectedEmotion] = useState<string>("default");
  const [selectedTemplate, setSelectedTemplate] = useState<FancyTemplateId>("sticker");
  const [selectedPopupTemplate, setSelectedPopupTemplate] = useState<PopupTemplateId>("auto");
  const [outputAspect, setOutputAspect] = useState<"landscape" | "portrait">("landscape");
  const [previewVoice, setPreviewVoice] = useState<{ id: string; name: string } | null>(null);
  const [voices, setVoices] = useState<VoiceOption[]>(BUILTIN_MANDARIN_VOICES);
  const [script, setScript] = useState<string>("");
  const [clipCount, setClipCount] = useState<string>("1");
  const [clipDialogOpen, setClipDialogOpen] = useState(false);
  const [enableVoiceover, setEnableVoiceover] = useState(true);
  const [burnSubtitles, setBurnSubtitles] = useState(true);
  const [voiceoverTopic, setVoiceoverTopic] = useState("");
  const [targetSeconds, setTargetSeconds] = useState("");
  const [voiceToken, setVoiceToken] = useState(DEFAULT_ACCESS_TOKEN);
  const [loadingVoices, setLoadingVoices] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [popupLeadTime, setPopupLeadTime] = useState<number>(0.18);
  const [popupMinDuration, setPopupMinDuration] = useState<number>(0.55);
  const [popupMergeGap, setPopupMergeGap] = useState<number>(0.1);
  const [popupEnabled, setPopupEnabled] = useState<boolean>(true);

  useEffect(() => {
    let active = true;
    const loadSettings = async () => {
      try {
        const resp = await fetch("/api/settings");
        const data = await resp.json();
        if (!active) return;
        if (data?.success && typeof data?.settings?.voiceToken === "string") {
          const cachedToken = String(data.settings.voiceToken || "").trim();
          setVoiceToken(cachedToken || DEFAULT_ACCESS_TOKEN);
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
        headers: { "Content-Type": "application/json; charset=utf-8" },
        body: JSON.stringify({ voiceToken: tokenToSave }),
      });
    } catch {
      // Ignore save errors.
    }
  };

  const voiceSelectorVoices = useMemo(() => {
    return voices.length ? voices : BUILTIN_MANDARIN_VOICES;
  }, [voices]);

  const voiceNameMap = useMemo(() => {
    const map: Record<string, string> = {};
    voiceSelectorVoices.forEach((item) => {
      map[item.id] = item.name;
    });
    return map;
  }, [voiceSelectorVoices]);

  const selectedVoiceEmotionOptions = useMemo(() => {
    const item = voiceSelectorVoices.find((voice) => voice.id === selectedVoice);
    return item?.emotions || [];
  }, [selectedVoice, voiceSelectorVoices]);

  useEffect(() => {
    setSelectedEmotion("default");
  }, [selectedVoice]);

  useEffect(() => {
    if (script.trim()) {
      setBurnSubtitles(true);
    }
  }, [script]);

  const handleBurnSubtitlesChange = (checked: boolean) => {
    if (checked && !script.trim() && !enableVoiceover) {
      toast.error("请先输入口播文案，或开启自动AI口播。");
      return;
    }
    setBurnSubtitles(checked);
  };

  const handleVoicePreview = (voiceId: string) => {
    setPreviewVoice({ id: voiceId, name: voiceNameMap[voiceId] || voiceId });
  };

  const templateNameMap: Record<FancyTemplateId, string> = {
    sticker: "贴纸",
    neon: "霓虹",
    karaoke: "卡拉 OK",
    subtitle: "电影字幕",
    default: "基础",
    transparent_outline: "透明描边",
    transparent_neon: "透明霓虹",
    transparent_subtitle: "透明字幕",
    promo_tag: "促销价签",
    brand_banner: "品牌横幅",
    news_flash: "快讯条",
    luxury_minimal: "高端极简",
    yellow_black_bold: "黄字黑粗描边",
    yellow_black_glow: "金黄发光描边",
    yellow_orange_flash: "橙黄高亮字",
    black_plate_yellow: "黑底黄字牌",
    popup_zoom_gold: "弹出-金色爆炸",
    popup_bounce_red: "弹出-红色冲击",
    popup_neon_flash: "弹出-霓虹闪烁",
    popup_explosion: "弹出-炸裂特效",
    popup_scale_purple: "弹出-紫色缩放",
    popup_shake_yellow: "弹出-黄色震动",
    popup_half_bg_gold: "弹出-半背景金字",
  };
  const popupTemplateOptions: { value: PopupTemplateId; label: string }[] = [
    { value: "auto", label: "自动（跟随花字模板）" },
    { value: "popup_zoom_gold", label: "弹出-金色爆炸" },
    { value: "popup_bounce_red", label: "弹出-红色冲击" },
    { value: "popup_neon_flash", label: "弹出-霓虹闪烁" },
    { value: "popup_explosion", label: "弹出-炸裂特效" },
    { value: "popup_scale_purple", label: "弹出-紫色缩放" },
    { value: "popup_shake_yellow", label: "弹出-黄色震动" },
    { value: "popup_half_bg_gold", label: "弹出-半背景金字" },
  ];

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
    if (!hasScript && (!Number.isFinite(secs) || secs <= 0)) {
      toast.error("请先输入剪辑秒数。");
      return;
    }
    if (enableVoiceover && !hasScript && !hasTopic) {
      toast.error("请先输入文案主题，或关闭 AI 口播后按秒数剪辑。");
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
      headers: { "Content-Type": "application/json; charset=utf-8" },
      body: JSON.stringify({ requirement, seconds: 40 }),
    });
    const data = await resp.json();
    if (!data.success) {
      throw new Error(data.message || "文案生成失败");
    }
    return String(data.script || "");
  }

  const fetchVoices = async () => {
    await persistSettings(voiceToken);
    setVoices(BUILTIN_MANDARIN_VOICES);
    toast.success(`已加载内置音色 ${BUILTIN_MANDARIN_VOICES.length} 个`);
  };

  const handleExport = async () => {
    if (selectedFiles.length === 0) {
      toast.error("请先选择素材目录");
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
      const useVoiceover = enableVoiceover && Boolean(scriptToUse);
      const parsedTargetSeconds = Number.parseInt(targetSeconds, 10);
      if (!useVoiceover && (!Number.isFinite(parsedTargetSeconds) || parsedTargetSeconds <= 0)) {
        throw new Error("请先输入剪辑秒数。");
      }
      if (enableVoiceover && !useVoiceover) {
        throw new Error("请先输入文案主题，或关闭 AI 口播后按秒数剪辑。");
      }
      const targetDuration = !useVoiceover ? parsedTargetSeconds : undefined;

      const uploadForm = new FormData();
      selectedFiles.forEach((file) => uploadForm.append("files", file));
      const uploadResp = await fetch("/api/upload-clips", { method: "POST", body: uploadForm });
      const uploadData = await uploadResp.json();
      if (!uploadData.success) {
        throw new Error(uploadData.message || "素材上传失败");
      }
      const clips: string[] = Array.isArray(uploadData.clips) ? uploadData.clips : [];
      let bgmTracks: string[] = [];
      if (selectedBgmFiles.length > 0) {
        const bgmForm = new FormData();
        selectedBgmFiles.forEach((file) => bgmForm.append("files", file));
        const bgmResp = await fetch("/api/upload-bgm", { method: "POST", body: bgmForm });
        const bgmData = await bgmResp.json();
        if (!bgmData.success) {
          throw new Error(bgmData.message || "背景音乐上传失败");
        }
        bgmTracks = Array.isArray(bgmData.tracks) ? bgmData.tracks : [];
      }
      const count = Math.max(1, Number.parseInt(clipCount, 10) || 1);

      for (let i = 0; i < count; i += 1) {
        const outputName = count === 1 ? "mixed_output.mp4" : `mixed_output_${i + 1}.mp4`;
        const resolution = outputAspect === "portrait" ? [1080, 1920] : [1920, 1080];
        const mixResp = await fetch("/api/mix", {
          method: "POST",
          headers: { "Content-Type": "application/json; charset=utf-8" },
          body: JSON.stringify({
            clips,
            outputName,
            resolution,
            transition: "fade",
            transitionDuration: 1.0,
            randomizeOrder: true,
            bgmTracks,
            bgmVolume: 0.45,
            overlayText: "",
            targetDuration,
              voiceover: {
                enabled: useVoiceover,
                text: scriptToUse,
                token: voiceToken,
                voiceType: selectedVoice,
                speaker: selectedVoice,
                ...(selectedEmotion !== "default" ? { emotion: selectedEmotion } : {}),
                originalAudioMixLevel: 0.0,
                subtitlesEnabled: burnSubtitles,
                subtitleTemplate: selectedTemplate,
                subtitleEffect: ["yellow_black_bold", "yellow_black_glow", "yellow_orange_flash", "black_plate_yellow"].includes(selectedTemplate) ? "none" : "pop",
                popupEnabled,
                popupTemplate: selectedPopupTemplate,
                subtitleFontsize: 48,
                subtitleFontcolor: "white",
                matchVideoDuration: true,
                popupLeadTime,
                popupMinDuration,
                popupMergeGap,
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

  const handleBgmFolderChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const allFiles = Array.from(event.target.files || []);
    const audioFiles = allFiles.filter((file) => {
      const name = file.name.toLowerCase();
      return [".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg"].some((suffix) => name.endsWith(suffix));
    });

    if (audioFiles.length === 0) {
      toast.error("该目录没有可用的音频文件");
      event.currentTarget.value = "";
      return;
    }

    const firstFile = audioFiles[0];
    const rel = (firstFile as File & { webkitRelativePath?: string }).webkitRelativePath || firstFile.name;
    const folder = rel.includes("/") ? rel.split("/")[0] : "已选择背景音乐";
    setBgmFolderName(folder);
    setSelectedBgmFiles(audioFiles);
    event.currentTarget.value = "";
  };

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
                <h2 className="bg-gradient-to-r from-purple-700 to-pink-700 bg-clip-text text-lg font-bold text-transparent">花字展示</h2>
              </div>
              <div className="relative">
                <FancyTextShowcase selectedTemplate={selectedTemplate} onSelectTemplate={setSelectedTemplate} />
              </div>
            </div>

            <div className="relative overflow-hidden rounded-2xl border border-gray-200/60 bg-white/85 p-6 shadow-[0_8px_32px_rgba(0,0,0,0.08)] backdrop-blur-2xl">
              <div className="absolute bottom-0 left-0 h-72 w-72 rounded-full bg-gradient-to-tr from-amber-200/20 to-transparent blur-3xl" />
              <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/60 to-transparent" />
              <div className="relative mb-4 flex items-center gap-2.5">
                <div className="h-7 w-1 rounded-full bg-gradient-to-b from-amber-500 via-orange-500 to-red-500 shadow-lg shadow-amber-500/40" />
                <h2 className="bg-gradient-to-r from-amber-700 to-orange-700 bg-clip-text text-lg font-bold text-transparent">弹出模板展示</h2>
              </div>
              <div className="relative">
                <PopupTemplateShowcase selectedTemplate={selectedPopupTemplate} onSelectTemplate={setSelectedPopupTemplate} />
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
                {selectedVoiceEmotionOptions.length > 0 && (
                  <div className="mt-3 space-y-2 rounded-xl border border-cyan-200 bg-cyan-50/40 p-3">
                    <Label className="text-sm font-semibold text-cyan-800">情感/风格</Label>
                    <Select value={selectedEmotion} onValueChange={setSelectedEmotion}>
                      <SelectTrigger className="border-cyan-200 bg-white/90">
                        <SelectValue placeholder="选择情感（默认通用）" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="default">通用（默认）</SelectItem>
                        {selectedVoiceEmotionOptions.map((item) => (
                          <SelectItem key={item.value} value={item.value}>
                            {item.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                )}
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
                  <span className="font-bold text-purple-700">{templateNameMap[selectedTemplate]}</span>
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

              <div className="relative mt-4 space-y-2">
                <Label className="text-sm font-semibold text-gray-700">输出画幅</Label>
                <Select value={outputAspect} onValueChange={(v) => setOutputAspect(v as "landscape" | "portrait")}>
                  <SelectTrigger className="border-blue-200 bg-gradient-to-r from-blue-50/50 to-cyan-50/50 font-semibold shadow-sm focus:border-blue-500 focus:ring-blue-500">
                    <SelectValue placeholder="选择画幅" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="landscape">横版 16:9（1920x1080）</SelectItem>
                    <SelectItem value="portrait">竖版 9:16（1080x1920）</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="relative mt-4 space-y-2 rounded-xl border border-sky-200/60 bg-gradient-to-r from-sky-50/80 to-cyan-50/80 p-3 backdrop-blur">
                <Label htmlFor="bgm-folder-upload" className="cursor-pointer text-sm font-bold text-gray-800">
                  背景音乐目录（可选）
                </Label>
                <input
                  id="bgm-folder-upload"
                  type="file"
                  onChange={handleBgmFolderChange}
                  onClick={(e) => {
                    e.currentTarget.value = "";
                  }}
                  className="hidden"
                  {...({ webkitdirectory: "", directory: "" } as never)}
                  multiple
                  accept=".mp3,.wav,.m4a,.aac,.flac,.ogg"
                />
                <label htmlFor="bgm-folder-upload" className="block cursor-pointer rounded-lg border border-sky-300 bg-white/90 px-3 py-2 text-center text-sm font-semibold text-sky-700 hover:bg-sky-50">
                  {selectedBgmFiles.length > 0 ? "更换背景音乐目录" : "选择背景音乐目录"}
                </label>
                <p className="text-xs text-gray-600">
                  {selectedBgmFiles.length > 0
                    ? `${bgmFolderName || "已选择"} · 共 ${selectedBgmFiles.length} 首，每条视频随机选 1 首`
                    : "不选择则不额外叠加背景音乐"}
                </p>
              </div>

              <div className="relative mt-4 flex items-center justify-between rounded-xl border border-purple-200/60 bg-gradient-to-r from-purple-50/80 to-pink-50/80 p-3 backdrop-blur">
                <div className="space-y-0.5">
                  <Label htmlFor="enable-voiceover-main" className="cursor-pointer text-sm font-bold text-gray-800">
                    启用口播
                  </Label>
                  <p className="text-xs text-gray-600">开启后会合成语音</p>
                </div>
                <Switch id="enable-voiceover-main" checked={enableVoiceover} onCheckedChange={setEnableVoiceover} />
              </div>
              <div className="relative mt-3 flex items-center justify-between rounded-xl border border-emerald-200/60 bg-gradient-to-r from-emerald-50/80 to-teal-50/80 p-3 backdrop-blur">
                <div className="space-y-0.5">
                  <Label htmlFor="burn-subtitles-main" className="cursor-pointer text-sm font-bold text-gray-800">
                    烧录字幕
                  </Label>
                  <p className="text-xs text-gray-600">与口播开关分开控制</p>
                </div>
                <Switch id="burn-subtitles-main" checked={burnSubtitles} onCheckedChange={handleBurnSubtitlesChange} />
              </div>

              <div className="relative mt-3 space-y-3 rounded-xl border border-amber-200/60 bg-gradient-to-r from-amber-50/80 to-orange-50/80 p-3 backdrop-blur">
                <p className="text-sm font-bold text-amber-800">弹出字幕节奏（推荐默认值）</p>
                <div className="flex items-center justify-between rounded-lg border border-amber-300/70 bg-white/70 p-2">
                  <Label htmlFor="popup-enabled" className="cursor-pointer text-xs font-semibold text-gray-700">
                    启用弹出特效
                  </Label>
                  <Switch id="popup-enabled" checked={popupEnabled} onCheckedChange={setPopupEnabled} />
                </div>
                <div className="space-y-2">
                  <Label className="text-xs font-semibold text-gray-700">弹出模板（独立）</Label>
                  <Select value={selectedPopupTemplate} onValueChange={(v) => setSelectedPopupTemplate(v as PopupTemplateId)}>
                    <SelectTrigger className="h-9 border-amber-300 bg-white/90 text-xs font-semibold text-amber-800">
                      <SelectValue placeholder="选择弹出模板" />
                    </SelectTrigger>
                    <SelectContent>
                      {popupTemplateOptions.map((item) => (
                        <SelectItem key={item.value} value={item.value}>
                          {item.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => {
                    setPopupLeadTime(0.18);
                    setPopupMinDuration(0.55);
                    setPopupMergeGap(0.1);
                  }}
                  className="h-8 border-amber-300 bg-white/80 px-3 text-xs font-semibold text-amber-700 hover:bg-amber-50"
                >
                  恢复推荐值
                </Button>

                <div className="space-y-1.5">
                  <div className="flex items-center justify-between">
                    <Label className="text-xs font-semibold text-gray-700">提前弹出</Label>
                    <span className="text-xs font-bold text-amber-700">{popupLeadTime.toFixed(2)}s</span>
                  </div>
                  <input
                    type="range"
                    min={0}
                    max={0.5}
                    step={0.01}
                    value={popupLeadTime}
                    onChange={(e) => setPopupLeadTime(Number(e.target.value))}
                    className="w-full accent-amber-600"
                  />
                </div>

                <div className="space-y-1.5">
                  <div className="flex items-center justify-between">
                    <Label className="text-xs font-semibold text-gray-700">最短停留</Label>
                    <span className="text-xs font-bold text-amber-700">{popupMinDuration.toFixed(2)}s</span>
                  </div>
                  <input
                    type="range"
                    min={0.2}
                    max={1.2}
                    step={0.01}
                    value={popupMinDuration}
                    onChange={(e) => setPopupMinDuration(Number(e.target.value))}
                    className="w-full accent-amber-600"
                  />
                </div>

                <div className="space-y-1.5">
                  <div className="flex items-center justify-between">
                    <Label className="text-xs font-semibold text-gray-700">联动合并间隔</Label>
                    <span className="text-xs font-bold text-amber-700">{popupMergeGap.toFixed(2)}s</span>
                  </div>
                  <input
                    type="range"
                    min={0}
                    max={0.3}
                    step={0.01}
                    value={popupMergeGap}
                    onChange={(e) => setPopupMergeGap(Number(e.target.value))}
                    className="w-full accent-amber-600"
                  />
                </div>

                <p className="text-[11px] text-gray-600">字幕默认贴近底部安全区显示，尽量不挡住画面主体。</p>
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
            <DialogDescription className="font-medium text-gray-600">配置剪辑参数，口播与烧录字幕可分别控制</DialogDescription>
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

            {!script.trim() && (
              <div className="flex items-center justify-between rounded-xl border border-purple-200/60 bg-gradient-to-r from-purple-50/80 to-pink-50/80 p-4 backdrop-blur">
                <div className="space-y-0.5">
                  <Label htmlFor="enable-voiceover" className="cursor-pointer text-sm font-bold text-gray-800">
                    自动AI口播
                  </Label>
                  <p className="text-xs text-gray-600">无文案时可自动生成口播文案并配音</p>
                </div>
                <Switch
                  id="enable-voiceover"
                  checked={enableVoiceover}
                  onCheckedChange={setEnableVoiceover}
                  className="scale-125 data-[state=checked]:bg-gradient-to-r data-[state=checked]:from-purple-600 data-[state=checked]:to-pink-600 data-[state=unchecked]:bg-gray-300"
                />
              </div>
            )}

            {enableVoiceover && !script.trim() && (
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

            <div className="flex items-center justify-between rounded-xl border border-emerald-200/60 bg-gradient-to-r from-emerald-50/80 to-teal-50/80 p-4 backdrop-blur">
              <div className="space-y-0.5">
                <Label htmlFor="burn-subtitles" className="cursor-pointer text-sm font-bold text-gray-800">
                  烧录字幕
                </Label>
                <p className="text-xs text-gray-600">与自动AI口播分开控制</p>
              </div>
              <Switch id="burn-subtitles" checked={burnSubtitles} onCheckedChange={handleBurnSubtitlesChange} className="scale-125" />
            </div>

            {!script.trim() && (
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



