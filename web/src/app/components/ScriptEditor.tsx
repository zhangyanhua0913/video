import { useState } from "react";
import { Check, Copy, FileText, Sparkles, Wand2 } from "lucide-react";
import { Button } from "./ui/button";
import { Textarea } from "./ui/textarea";
import { Label } from "./ui/label";
import { Input } from "./ui/input";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "./ui/dialog";
import { toast } from "sonner";

interface ScriptEditorProps {
  script: string;
  onScriptChange: (script: string) => void;
  onGenerateScript?: (topic: string) => Promise<string>;
}

export function ScriptEditor({ script, onScriptChange, onGenerateScript }: ScriptEditorProps) {
  const [topic, setTopic] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [isPolishing, setIsPolishing] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleGenerate = async () => {
    if (!topic.trim()) {
      toast.error("请输入视频主题");
      return;
    }
    setIsGenerating(true);
    try {
      let content = "";
      if (onGenerateScript) {
        content = await onGenerateScript(topic.trim());
      } else {
        content = `这期我们围绕“${topic.trim()}”来聊聊重点内容，带你快速抓住核心信息。`;
      }
      onScriptChange(content);
      setDialogOpen(false);
      toast.success("口播文案已生成");
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "文案生成失败");
    } finally {
      setIsGenerating(false);
    }
  };

  const handlePolish = async () => {
    if (!script.trim()) {
      toast.error("请先输入口播文本");
      return;
    }
    setIsPolishing(true);
    await new Promise((resolve) => setTimeout(resolve, 600));
    const polished = script
      .replace(/\s+/g, " ")
      .replace(/，/g, "，")
      .replace(/。/g, "。")
      .trim();
    onScriptChange(polished);
    setIsPolishing(false);
    toast.success("文案润色完成");
  };

  const handleCopy = async () => {
    await navigator.clipboard.writeText(script);
    setCopied(true);
    toast.success("已复制到剪贴板");
    setTimeout(() => setCopied(false), 1800);
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="relative">
            <div className="absolute inset-0 rounded-xl bg-purple-400/30 blur-md" />
            <div className="relative rounded-xl bg-gradient-to-br from-purple-500 to-pink-600 p-1.5 shadow-md">
              <FileText className="h-4 w-4 text-white drop-shadow" />
            </div>
          </div>
          <Label className="bg-gradient-to-r from-purple-700 to-pink-700 bg-clip-text text-base font-bold text-transparent">口播文案</Label>
        </div>

        <div className="flex gap-2">
          <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
            <DialogTrigger asChild>
              <Button variant="outline" size="sm" className="gap-1.5 border-purple-200 font-semibold text-purple-700 shadow-sm transition-all hover:border-purple-400 hover:bg-purple-50">
                <Sparkles className="h-3.5 w-3.5" />
                生成
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-xl border-gray-200 bg-white shadow-2xl">
              <DialogHeader>
                <DialogTitle className="bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-xl font-bold text-transparent">AI 生成口播文案</DialogTitle>
                <DialogDescription className="font-medium text-gray-600">输入主题后自动生成约 40 秒口播文案。</DialogDescription>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div className="space-y-2">
                  <Label htmlFor="topic" className="font-semibold text-gray-700">
                    视频主题
                  </Label>
                  <Input
                    id="topic"
                    placeholder="例如：智能剪辑效率提升"
                    value={topic}
                    onChange={(e) => setTopic(e.target.value)}
                    className="border-purple-200 bg-purple-50/50 shadow-sm focus:border-purple-500 focus:ring-purple-500"
                  />
                </div>
                <div className="flex gap-2">
                  <Button
                    onClick={handleGenerate}
                    disabled={isGenerating}
                    className="flex-1 bg-gradient-to-r from-purple-600 to-pink-600 font-semibold shadow-lg shadow-purple-500/30 hover:from-purple-700 hover:to-pink-700"
                  >
                    {isGenerating ? "生成中..." : "生成文案"}
                  </Button>
                  <Button variant="outline" onClick={() => setDialogOpen(false)} className="flex-1 border-gray-300 font-semibold hover:bg-gray-50">
                    取消
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>

          <Button
            variant="outline"
            size="sm"
            className="gap-1.5 border-cyan-200 font-semibold text-cyan-700 shadow-sm transition-all hover:border-cyan-400 hover:bg-cyan-50"
            onClick={handlePolish}
            disabled={isPolishing || !script.trim()}
          >
            <Wand2 className="h-3.5 w-3.5" />
            {isPolishing ? "润色中..." : "润色"}
          </Button>

          <Button
            variant="outline"
            size="sm"
            className="gap-1.5 border-gray-200 font-semibold text-gray-600 shadow-sm transition-all hover:border-gray-400 hover:bg-gray-50"
            onClick={handleCopy}
            disabled={!script.trim()}
          >
            {copied ? (
              <>
                <Check className="h-3.5 w-3.5" />
                已复制
              </>
            ) : (
              <>
                <Copy className="h-3.5 w-3.5" />
                复制
              </>
            )}
          </Button>
        </div>
      </div>

      <div className="relative">
        <Textarea
          value={script}
          onChange={(e) => onScriptChange(e.target.value)}
          placeholder="在此输入或生成口播文案..."
          className="min-h-[320px] resize-none border-purple-200 bg-gradient-to-br from-purple-50/60 to-pink-50/60 font-medium text-gray-800 shadow-inner backdrop-blur placeholder:text-gray-400 focus:border-purple-400 focus:ring-purple-400"
        />
        <div className="absolute bottom-3 right-3 rounded-lg border border-purple-200/80 bg-white/95 px-2.5 py-1 text-xs font-bold text-purple-700 shadow-sm backdrop-blur">
          {script.length} 字
        </div>
      </div>

      <div className="rounded-xl border border-indigo-200/60 bg-gradient-to-r from-indigo-100/70 to-purple-100/70 p-2.5 shadow-sm backdrop-blur">
        <p className="text-xs font-semibold text-indigo-700">提示：可先自动生成文案，再手动微调。最终导出会按文案长度自动匹配视频时长。</p>
      </div>
    </div>
  );
}
