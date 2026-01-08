import { useState, useEffect, useRef } from 'react';
import { FileText, Folder, Table, Search, Upload, RefreshCw, ChevronRight, ChevronDown, MoreVertical, Eye, Trash2, Download, Loader2, AlertCircle, X, FileUp, FolderUp } from 'lucide-react';

// Debug helper
declare global {
  interface Window {
    _debugLogs: string[];
  }
}
window._debugLogs = window._debugLogs || [];
const debugLog = (msg: string) => {
  window._debugLogs.push(`[${new Date().toISOString()}] ${msg}`);
  console.log(msg);
};

import { AppLayout } from '@/components/layout/AppLayout';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Textarea } from '@/components/ui/textarea';
import { cn } from '@/lib/utils';
import { useFiles, useFileStats, type FileItem } from '@/hooks/useFiles';
import { getApiSettings } from './Settings';
import { toast } from 'sonner';
import { useProjectStore } from '@/stores/projectStore';
// Fallback mock data
const mockFiles: FileItem[] = [
  {
    id: '1', name: 'source', type: 'folder', modified: '2 days ago', status: 'processed',
    children: [
      { id: '1-1', name: 'transactions.sql', type: 'file', fileType: 'sql', size: '24 KB', modified: '2 hours ago', status: 'processed' },
      { id: '1-2', name: 'customers.sql', type: 'file', fileType: 'sql', size: '18 KB', modified: '5 hours ago', status: 'processed' },
    ],
  },
  {
    id: '2', name: 'staging', type: 'folder', modified: '1 day ago', status: 'processed',
    children: [
      { id: '2-1', name: 'stg_orders.sql', type: 'file', fileType: 'sql', size: '32 KB', modified: '3 hours ago', status: 'processed' },
      { id: '2-2', name: 'stg_inventory.sql', type: 'file', fileType: 'sql', size: '28 KB', modified: '6 hours ago', status: 'pending' },
    ],
  },
  {
    id: '3', name: 'analytics', type: 'folder', modified: '3 hours ago', status: 'processed',
    children: [
      { id: '3-1', name: 'revenue_summary.sql', type: 'file', fileType: 'sql', size: '45 KB', modified: '1 hour ago', status: 'processed' },
      { id: '3-2', name: 'customer_segments.sql', type: 'file', fileType: 'sql', size: '38 KB', modified: '4 hours ago', status: 'error' },
    ],
  },
  { id: '4', name: 'config.json', type: 'file', fileType: 'json', size: '2 KB', modified: '1 week ago', status: 'processed' },
];

const mockStats = { total: 1284, processed: 1241, pending: 38, errors: 5 };

const defaultAllowedExtensions = ['.sql', '.ddl', '.csv', '.json'];
const defaultMaxFileSizeMb = 50;

const getFileIcon = (type: string, fileType?: string) => {
  if (type === 'folder') return Folder;
  if (fileType === 'sql' || fileType === 'ddl') return FileText;
  return Table;
};

const getStatusColor = (status: string) => {
  switch (status) {
    case 'processed': return 'bg-green-500';
    case 'pending': return 'bg-yellow-500';
    case 'error': return 'bg-red-500';
    default: return 'bg-gray-500';
  }
};

function FileTreeItem({ item, level = 0 }: { item: FileItem; level?: number }) {
  const [isExpanded, setIsExpanded] = useState(level === 0);
  const Icon = getFileIcon(item.type, item.fileType);
  const hasChildren = item.children && item.children.length > 0;

  return (
    <div>
      <div
        className={cn(
          "flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-muted/50 transition-colors cursor-pointer group",
          level > 0 && "ml-4"
        )}
        onClick={() => hasChildren && setIsExpanded(!isExpanded)}
      >
        {hasChildren ? (
          isExpanded ? <ChevronDown className="w-4 h-4 text-muted-foreground" /> : <ChevronRight className="w-4 h-4 text-muted-foreground" />
        ) : (
          <div className="w-4" />
        )}
        <div className={cn("p-1.5 rounded", item.type === 'folder' ? 'bg-primary/10' : 'bg-muted')}>
          <Icon className={cn("w-4 h-4", item.type === 'folder' ? 'text-primary' : 'text-muted-foreground')} />
        </div>
        <div className="flex-1 min-w-0">
          <p className="font-medium text-sm truncate">{item.name}</p>
          <p className="text-xs text-muted-foreground">{item.size || `${item.children?.length || 0} items`} • {item.modified}</p>
        </div>
        <div className={cn("w-2 h-2 rounded-full", getStatusColor(item.status))} />
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon" className="h-7 w-7 opacity-0 group-hover:opacity-100">
              <MoreVertical className="w-4 h-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem><Eye className="w-4 h-4 mr-2" /> View Lineage</DropdownMenuItem>
            <DropdownMenuItem><Download className="w-4 h-4 mr-2" /> Download</DropdownMenuItem>
            <DropdownMenuItem className="text-destructive"><Trash2 className="w-4 h-4 mr-2" /> Delete</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
      {hasChildren && isExpanded && (
        <div className="border-l border-border ml-5">
          {item.children!.map((child) => (
            <FileTreeItem key={child.id} item={child} level={level + 1} />
          ))}
        </div>
      )}
    </div>
  );
}

export default function Files() {
  debugLog('[Files] Rendering component');
  const [searchQuery, setSearchQuery] = useState('');
  const [useMockData, setUseMockData] = useState(false);
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [allowedExtensions, setAllowedExtensions] = useState<string[]>(defaultAllowedExtensions);
  const [maxFileSizeMb, setMaxFileSizeMb] = useState<number>(defaultMaxFileSizeMb);
  const [ingestionInstructions, setIngestionInstructions] = useState<string>('');
  const [projectIdInput, setProjectIdInput] = useState<string>('');
  const fileInputRef = useRef<HTMLInputElement>(null);
  const folderInputRef = useRef<HTMLInputElement>(null);
  const { activeProjectId } = useProjectStore();
  const { data: files, isLoading: filesLoading, isError: filesError, refetch } = useFiles();
  const { data: stats, isLoading: statsLoading, isError: statsError } = useFileStats();

  const displayFiles = useMockData || filesError ? mockFiles : (files || mockFiles);
  const displayStats = useMockData || statsError ? mockStats : (stats || mockStats);

  useEffect(() => {
    if (filesError) setUseMockData(true);
  }, [filesError]);

  // Mirror active project from store into the modal input
  useEffect(() => {
    if (activeProjectId && !projectIdInput) {
      setProjectIdInput(activeProjectId);
    }
  }, [activeProjectId, projectIdInput]);

  // Fetch upload configuration to mirror backend policies
  useEffect(() => {
    const fetchConfig = async () => {
      try {
        const { apiUrl, endpoints } = getApiSettings();
        const configPath =
          (endpoints as any).filesConfig ||
          `${(endpoints.filesUpload || '/api/v1/files/upload').replace(/\/upload$/, '')}/config`;
        const response = await fetch(`${apiUrl}${configPath}`);
        if (!response.ok) return;
        const data = await response.json();

        if (Array.isArray(data.allowed_extensions)) {
          const normalized = data.allowed_extensions.map((ext: string) =>
            ext.startsWith('.') ? ext.toLowerCase() : `.${ext.toLowerCase()}`
          );
          setAllowedExtensions(normalized);
        }
        if (typeof data.max_file_size_mb === 'number') {
          setMaxFileSizeMb(data.max_file_size_mb);
        }
      } catch (err) {
        console.warn('Failed to fetch upload config, using defaults', err);
      }
    };

    fetchConfig();
  }, []);

  const validateFile = (file: File) => {
    const ext = `.${file.name.split('.').pop()?.toLowerCase() || ''}`;
    const isAllowed = allowedExtensions.includes(ext);
    const maxBytes = maxFileSizeMb * 1024 * 1024;

    if (!isAllowed) {
      toast.error('Invalid file type', { description: `Allowed: ${allowedExtensions.join(', ')}` });
      return false;
    }
    if (file.size > maxBytes) {
      toast.error('File too large', { description: `Max size: ${maxFileSizeMb} MB` });
      return false;
    }
    return true;
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const droppedFiles = Array.from(e.dataTransfer.files).filter(validateFile);

    if (droppedFiles.length > 0) {
      setSelectedFiles(prev => [...prev, ...droppedFiles]);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const newFiles = Array.from(e.target.files).filter(validateFile);
      if (newFiles.length > 0) {
        setSelectedFiles(prev => [...prev, ...newFiles]);
      }
      e.target.value = ''; // Reset to allow re-selecting same files
    }
  };

  const removeFile = (index: number) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const { activeProjectId } = useProjectStore();

  const handleUpload = async () => {
    if (selectedFiles.length === 0) return;

    const targetProjectId = projectIdInput.trim();
    if (!targetProjectId) {
      toast.error('No project selected', { description: 'Enter a valid project ID before uploading.' });
      return;
    }

    setIsUploading(true);

    const { apiUrl, endpoints } = getApiSettings();
    const uploadEndpoint = endpoints.filesUpload || '/api/v1/files/upload';

    try {
      const formData = new FormData();
      selectedFiles.forEach(file => formData.append('files', file));
      formData.append('project_id', targetProjectId);
      formData.append('repository_name', 'Manual Uploads'); // Default for now
      if (ingestionInstructions.trim()) {
        formData.append('instructions', ingestionInstructions.trim());
      }

      const response = await fetch(`${apiUrl}${uploadEndpoint}`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Upload failed (${response.status}): ${errorText || 'Unknown error'}`);
      }

      toast.success('Files uploaded', { description: `${selectedFiles.length} file(s) uploaded successfully` });
      setSelectedFiles([]);
      setIngestionInstructions('');
      setUploadModalOpen(false);
      refetch();
    } catch (error) {
      console.error('Upload error:', error);
      toast.error('Upload failed', { description: 'Could not upload files. Check backend connection.' });
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <AppLayout>
      <div className="p-6 space-y-6 animate-slide-up">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold tracking-tight">Files</h1>
            <p className="text-muted-foreground">Browse and manage ingested SQL files and schemas</p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => refetch()}>
              <RefreshCw className={cn("w-4 h-4 mr-2", filesLoading && "animate-spin")} />
              Sync
            </Button>
            <Button onClick={() => setUploadModalOpen(true)} data-testid="upload-button">
              <Upload className="w-4 h-4 mr-2" />
              Upload
            </Button>
          </div>
        </div>

        {/* Upload Modal */}
        <Dialog open={uploadModalOpen} onOpenChange={setUploadModalOpen}>
          <DialogContent className="sm:max-w-lg">
            <DialogHeader>
              <DialogTitle>Upload Files</DialogTitle>
              <DialogDescription>
                Upload SQL, DDL, CSV, or JSON files for lineage processing
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-4">
              {/* Drop Zone */}
              <div
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
                className={cn(
                  "border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all",
                  dragActive
                    ? "border-primary bg-primary/5"
                    : "border-muted-foreground/25 hover:border-primary/50 hover:bg-muted/50"
                )}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  multiple
                  accept={allowedExtensions.join(',')}
                  onChange={handleFileSelect}
                  className="hidden"
                  data-testid="file-upload-input"
                />
                <input
                  ref={folderInputRef}
                  type="file"
                  // @ts-ignore - webkitdirectory is a valid attribute
                  webkitdirectory=""
                  directory=""
                  multiple
                  onChange={handleFileSelect}
                  className="hidden"
                />
                <FileUp className={cn(
                  "w-10 h-10 mx-auto mb-3 transition-colors",
                  dragActive ? "text-primary" : "text-muted-foreground"
                )} />
                <p className="text-sm font-medium">
                  {dragActive ? 'Drop files or folders here' : 'Drag & drop files/folders here'}
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  Supports {allowedExtensions.join(', ')} (max {maxFileSizeMb} MB each)
                </p>
              </div>

              {/* Upload Buttons */}
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  className="flex-1"
                  onClick={() => fileInputRef.current?.click()}
                >
                  <FileUp className="w-4 h-4 mr-2" />
                  Select Files
                </Button>
                <Button
                  variant="outline"
                  className="flex-1"
                  onClick={() => folderInputRef.current?.click()}
                >
                  <FolderUp className="w-4 h-4 mr-2" />
                  Select Folder
                </Button>
              </div>

              {/* Selected Files */}
              {selectedFiles.length > 0 && (
                <div className="space-y-2">
                  <p className="text-sm font-medium">{selectedFiles.length} file(s) selected</p>
                  <ScrollArea className="max-h-40">
                    <div className="space-y-1">
                      {selectedFiles.map((file, index) => (
                        <div key={index} className="flex items-center gap-2 p-2 rounded-lg bg-muted/50 group">
                          <FileText className="w-4 h-4 text-muted-foreground shrink-0" />
                          <span className="text-sm truncate flex-1">{file.name}</span>
                          <span className="text-xs text-muted-foreground">{(file.size / 1024).toFixed(1)} KB</span>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-6 w-6 opacity-0 group-hover:opacity-100"
                            onClick={(e) => { e.stopPropagation(); removeFile(index); }}
                          >
                            <X className="w-3 h-3" />
                          </Button>
                        </div>
                      ))}
                    </div>
                  </ScrollArea>
                </div>
              )}

              {/* Project ID */}
              <div className="space-y-2">
                <p className="text-sm font-medium">Project ID</p>
                <Input
                  value={projectIdInput}
                  onChange={(e) => setProjectIdInput(e.target.value)}
                  placeholder="Enter project ID (required)"
                />
                <p className="text-xs text-muted-foreground">
                  Uploads must be associated with an existing project. Ensure this ID exists on the backend.
                </p>
              </div>

              {/* Optional instructions for lineage */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <p className="text-sm font-medium">Optional instructions for lineage</p>
                  <span className="text-[11px] text-muted-foreground">{ingestionInstructions.length}/2000</span>
                </div>
                <Textarea
                  value={ingestionInstructions}
                  onChange={(e) => {
                    const next = e.target.value.slice(0, 2000);
                    if (next.length !== ingestionInstructions.length) {
                      setIngestionInstructions(next);
                    } else {
                      setIngestionInstructions(e.target.value);
                    }
                  }}
                  placeholder="Add context or guidance (Markdown/plain text) to improve lineage extraction (max 2000 chars)"
                  rows={3}
                  className="min-h-[72px]"
                />
              </div>

              {/* Actions */}
              <div className="flex justify-end gap-2 pt-2">
                <Button variant="outline" onClick={() => { setUploadModalOpen(false); setSelectedFiles([]); }}>
                  Cancel
                </Button>
                <Button onClick={handleUpload} disabled={selectedFiles.length === 0 || isUploading}>
                  {isUploading ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Uploading...
                    </>
                  ) : (
                    <>
                      <Upload className="w-4 h-4 mr-2" />
                      Upload {selectedFiles.length > 0 && `(${selectedFiles.length})`}
                    </>
                  )}
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>

        {useMockData && (
          <div className="bg-warning/10 border border-warning/20 rounded-lg px-4 py-2 flex items-center gap-2 text-sm">
            <AlertCircle className="w-4 h-4 text-warning" />
            <span>Using demo data - backend API unavailable</span>
            <Button variant="link" size="sm" className="ml-auto" onClick={() => { setUseMockData(false); refetch(); }}>
              Retry connection
            </Button>
          </div>
        )}

        {/* Search & Filters */}
        <div className="flex gap-4">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input placeholder="Search files..." className="pl-9" value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} />
          </div>
          <div className="flex gap-2">
            <Badge variant="secondary" className="cursor-pointer hover:bg-secondary/80">All</Badge>
            <Badge variant="outline" className="cursor-pointer hover:bg-muted">SQL</Badge>
            <Badge variant="outline" className="cursor-pointer hover:bg-muted">DDL</Badge>
            <Badge variant="outline" className="cursor-pointer hover:bg-muted">CSV</Badge>
          </div>
        </div>

        {/* Stats */}
        <div className="grid gap-4 sm:grid-cols-4">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-primary/10"><FileText className="w-5 h-5 text-primary" /></div>
                <div>
                  <p className="text-2xl font-bold">{statsLoading ? '...' : displayStats.total.toLocaleString()}</p>
                  <p className="text-xs text-muted-foreground">Total Files</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-green-500/10"><div className="w-5 h-5 rounded-full bg-green-500 flex items-center justify-center text-white text-xs font-bold">✓</div></div>
                <div>
                  <p className="text-2xl font-bold">{statsLoading ? '...' : displayStats.processed.toLocaleString()}</p>
                  <p className="text-xs text-muted-foreground">Processed</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-yellow-500/10"><div className="w-5 h-5 rounded-full bg-yellow-500" /></div>
                <div>
                  <p className="text-2xl font-bold">{statsLoading ? '...' : displayStats.pending}</p>
                  <p className="text-xs text-muted-foreground">Pending</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-red-500/10"><div className="w-5 h-5 rounded-full bg-red-500" /></div>
                <div>
                  <p className="text-2xl font-bold">{statsLoading ? '...' : displayStats.errors}</p>
                  <p className="text-xs text-muted-foreground">Errors</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* File Tree */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-lg">File Browser</CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            {filesLoading && !useMockData ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
              </div>
            ) : (
              <ScrollArea className="h-[400px]">
                <div className="p-4 space-y-1">
                  {displayFiles.map((file) => (
                    <FileTreeItem key={file.id} item={file} />
                  ))}
                </div>
              </ScrollArea>
            )}
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
}
