import { useState } from "react";
import { Folder, FolderOpen } from "lucide-react";
import { Button } from "./ui/button";

interface VideoUploaderProps {
  onVideoSelect: (file: File | null) => void;
  onFilesSelect?: (files: File[]) => void;
  selectedVideo: File | null;
}

export function VideoUploader({ onVideoSelect, onFilesSelect }: VideoUploaderProps) {
  const [folderName, setFolderName] = useState("");
  const [fileCount, setFileCount] = useState(0);

  const handleFolderChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || []);
    if (files.length === 0) {
      return;
    }

    const firstFile = files[0];
    const relativePath = firstFile.webkitRelativePath || firstFile.name;
    const folder = relativePath.includes("/") ? relativePath.split("/")[0] : "已选择素材";
    setFolderName(folder);
    setFileCount(files.length);
    onVideoSelect(firstFile);
    onFilesSelect?.(files);

    // Allow re-selecting the same folder next time.
    event.currentTarget.value = "";
  };

  return (
    <div className="w-full space-y-3">
      <div className="group relative overflow-hidden rounded-xl border-2 border-dashed border-indigo-300/80 bg-gradient-to-br from-indigo-50/60 to-purple-50/60 p-6 text-center shadow-inner backdrop-blur transition-all duration-300 hover:border-indigo-400">
        <div className="absolute inset-0 bg-gradient-to-br from-indigo-300/0 via-purple-300/10 to-indigo-300/0 opacity-0 transition-opacity duration-500 group-hover:opacity-100" />
        <input
          type="file"
          onChange={handleFolderChange}
          onClick={(e) => {
            // Ensure selecting the same folder still triggers onChange.
            e.currentTarget.value = "";
          }}
          className="hidden"
          id="folder-upload"
          {...({ webkitdirectory: "", directory: "" } as never)}
          multiple
          accept=".mp4,.mov,.mkv,.avi,.flv"
        />
        <label htmlFor="folder-upload" className="relative z-10 cursor-pointer">
          <div className="flex flex-col items-center gap-3">
            {folderName ? (
              <>
                <div className="relative">
                  <div className="absolute inset-0 rounded-xl bg-indigo-400/30 blur-lg" />
                  <div className="relative rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 p-3 shadow-lg">
                    <FolderOpen className="h-10 w-10 text-white drop-shadow" />
                  </div>
                </div>
                <div>
                  <p className="max-w-[240px] truncate text-sm font-bold text-gray-800">{folderName}</p>
                  <p className="mt-1 text-xs font-semibold text-indigo-600">共 {fileCount} 个视频文件</p>
                </div>
                <Button type="button" variant="outline" size="sm" className="border-indigo-300 font-semibold text-indigo-700 shadow-sm hover:border-indigo-500 hover:bg-indigo-50">
                  更换素材目录
                </Button>
              </>
            ) : (
              <>
                <div className="relative">
                  <div className="absolute inset-0 rounded-xl bg-indigo-400/20 blur-xl" />
                  <div className="relative rounded-xl border border-indigo-200/50 bg-gradient-to-br from-indigo-100/80 to-purple-100/80 p-4 shadow-sm">
                    <Folder className="h-10 w-10 text-indigo-500 drop-shadow-sm transition-colors group-hover:text-indigo-600" />
                  </div>
                </div>
                <div>
                  <p className="text-sm font-bold text-gray-800">选择视频素材目录</p>
                  <p className="mt-1 text-xs font-medium text-gray-500">批量导入目录中的视频文件</p>
                </div>
              </>
            )}
          </div>
        </label>
      </div>
    </div>
  );
}
