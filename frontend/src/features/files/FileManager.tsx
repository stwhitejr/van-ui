import {
  Box,
  Breadcrumbs,
  Dialog,
  DialogContent,
  DialogTitle,
  Grid2,
  IconButton,
  Link,
  Stack,
  TextField,
} from '@mui/material';
import {useState, useCallback} from 'react';
import Button from '@root/components/Button';
import Text from '@root/components/Text';
import Container from '@root/components/Container';
import PillBox from '@root/components/PillBox';
import {
  useListFilesQuery,
  useUploadFileMutation,
  useCreateFolderMutation,
  useDeleteFileMutation,
  FileItem,
} from './api';
import {createBaseUrl} from '@root/util/api';
import useToast from '@root/features/toast/useToast';
import RtkQueryGate from '@root/components/RtkQueryGate';

const BASE_URL = '/files';

interface FolderIconProps {
  width?: number;
  height?: number;
}

const FolderIcon = ({width = 24, height = 24}: FolderIconProps) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width={width}
    height={height}
    viewBox="0 0 24 24"
    fill="currentColor"
  >
    <path d="M10 4H4c-1.11 0-2 .89-2 2v12c0 1.11.89 2 2 2h16c1.11 0 2-.89 2-2V8c0-1.11-.89-2-2-2h-8l-2-2z" />
  </svg>
);

interface FileIconProps {
  width?: number;
  height?: number;
}

const FileIcon = ({width = 24, height = 24}: FileIconProps) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width={width}
    height={height}
    viewBox="0 0 24 24"
    fill="currentColor"
  >
    <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z" />
  </svg>
);

interface DeleteIconProps {
  width?: number;
  height?: number;
}

const DeleteIcon = ({width = 20, height = 20}: DeleteIconProps) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width={width}
    height={height}
    viewBox="0 0 24 24"
    fill="currentColor"
  >
    <path d="M19,4H15.5L14.5,3H9.5L8.5,4H5V6H19M6,19A2,2 0 0,0 8,21H16A2,2 0 0,0 18,19V7H6V19Z" />
  </svg>
);

const formatFileSize = (bytes?: number): string => {
  return (() => {
    if (!bytes) {
      return '';
    }
    return (() => {
      if (bytes < 1024) {
        return `${bytes} B`;
      }
      return (() => {
        if (bytes < 1024 * 1024) {
          return `${(bytes / 1024).toFixed(1)} KB`;
        }
        return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
      })();
    })();
  })();
};

const FileManager = () => {
  const [currentPath, setCurrentPath] = useState<string>('');
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [createFolderDialogOpen, setCreateFolderDialogOpen] = useState(false);
  const [folderName, setFolderName] = useState('');
  const [deleteConfirm, setDeleteConfirm] = useState<FileItem | null>(null);
  const toast = useToast();

  const {
    data: files,
    isLoading,
    refetch,
  } = useListFilesQuery(currentPath || undefined);

  const [uploadFile] = useUploadFileMutation();
  const [createFolder] = useCreateFolderMutation();
  const [deleteFile] = useDeleteFileMutation();

  const handleNavigate = useCallback((path: string) => {
    setCurrentPath(path);
  }, []);

  const handleFileClick = useCallback((file: FileItem) => {
    if (file.type === 'folder') {
      handleNavigate(file.path);
    } else {
      // Flask's path converter handles URL encoding, but we need to encode each segment
      const pathSegments = file.path.split('/').map(segment => encodeURIComponent(segment));
      const encodedPath = pathSegments.join('/');
      const url = `${createBaseUrl(BASE_URL)}/view/${encodedPath}`;
      window.open(url, '_blank');
    }
  }, [handleNavigate]);

  const handleUpload = useCallback(
    async (event: React.ChangeEvent<HTMLInputElement>) => {
      const fileList = event.target.files;
      if (!fileList || fileList.length === 0) {
        return;
      }

      try {
        for (let i = 0; i < fileList.length; i++) {
          const file = fileList[i];
          await uploadFile({
            file,
            folder: currentPath || undefined,
          }).unwrap();
        }
        toast({message: 'Files uploaded successfully', status: 'success'});
        setUploadDialogOpen(false);
        refetch();
      } catch (error: any) {
        toast({
          message: error?.data?.error || 'Failed to upload files',
          status: 'error',
        });
      }
      // Reset input
      event.target.value = '';
    },
    [currentPath, uploadFile, toast, refetch]
  );

  const handleCreateFolder = useCallback(async () => {
    if (!folderName.trim()) {
      toast({message: 'Folder name cannot be empty', status: 'error'});
      return;
    }

    try {
      await createFolder({
        name: folderName.trim(),
        path: currentPath || undefined,
      }).unwrap();
      toast({message: 'Folder created successfully', status: 'success'});
      setCreateFolderDialogOpen(false);
      setFolderName('');
      refetch();
    } catch (error: any) {
      toast({
        message: error?.data?.error || 'Failed to create folder',
        status: 'error',
      });
    }
  }, [folderName, currentPath, createFolder, toast, refetch]);

  const handleDelete = useCallback(
    async (file: FileItem) => {
      try {
        await deleteFile({path: file.path}).unwrap();
        toast({
          message: `${file.type === 'folder' ? 'Folder' : 'File'} deleted successfully`,
          status: 'success',
        });
        setDeleteConfirm(null);
        refetch();
      } catch (error: any) {
        toast({
          message: error?.data?.error || 'Failed to delete',
          status: 'error',
        });
      }
    },
    [deleteFile, toast, refetch]
  );

  const breadcrumbPaths = currentPath
    ? ['', ...currentPath.split('/')]
    : [''];

  const handleBreadcrumbClick = useCallback(
    (index: number) => {
      if (index === 0) {
        setCurrentPath('');
      } else {
        const pathParts = breadcrumbPaths.slice(1, index + 1);
        setCurrentPath(pathParts.join('/'));
      }
    },
    [breadcrumbPaths]
  );

  return (
    <Box p={2}>
      <Container
        title="File Manager"
        additional={
          <Stack direction="row" spacing={1}>
            <Button onClick={() => setCreateFolderDialogOpen(true)}>
              <Text size="body">New Folder</Text>
            </Button>
            <Button onClick={() => setUploadDialogOpen(true)}>
              <Text size="body">Upload</Text>
            </Button>
          </Stack>
        }
      >
        <Stack spacing={2}>
          <Breadcrumbs>
            {breadcrumbPaths.map((part, index) => (
              <Link
                key={index}
                component="button"
                variant="body1"
                onClick={() => handleBreadcrumbClick(index)}
                sx={{
                  cursor: 'pointer',
                  color: 'inherit',
                  textDecoration: 'none',
                  '&:hover': {
                    textDecoration: 'underline',
                  },
                }}
              >
                {index === 0 ? 'Root' : part}
              </Link>
            ))}
          </Breadcrumbs>

          <RtkQueryGate checkFetching isLoading={isLoading}>
            {files && files.length === 0 && (
              <Box textAlign="center" py={4}>
                <Text size="body">No files or folders</Text>
              </Box>
            )}
            {files && files.length > 0 && (
              <Grid2 container spacing={2}>
                {files.map((file) => (
                  <Grid2 key={file.path} size={{xs: 6, sm: 4, md: 3}}>
                    <PillBox
                      sx={{
                        p: 2,
                        cursor: 'pointer',
                        position: 'relative',
                        '&:hover': {
                          opacity: 0.8,
                        },
                      }}
                      onClick={() => handleFileClick(file)}
                    >
                      <Stack spacing={1} alignItems="center">
                        <Box>
                          {file.type === 'folder' ? (
                            <FolderIcon width={48} height={48} />
                          ) : (
                            <FileIcon width={48} height={48} />
                          )}
                        </Box>
                        <Box sx={{textAlign: 'center', wordBreak: 'break-word'}}>
                          <Text size="small">{file.name}</Text>
                        </Box>
                        {file.type === 'file' && file.size && (
                          <Box sx={{opacity: 0.7}}>
                            <Text size="small">{formatFileSize(file.size)}</Text>
                          </Box>
                        )}
                        <IconButton
                          size="small"
                          onClick={(e) => {
                            e.stopPropagation();
                            setDeleteConfirm(file);
                          }}
                          sx={{
                            position: 'absolute',
                            top: 4,
                            right: 4,
                            color: 'error.main',
                          }}
                        >
                          <DeleteIcon width={18} height={18} />
                        </IconButton>
                      </Stack>
                    </PillBox>
                  </Grid2>
                ))}
              </Grid2>
            )}
          </RtkQueryGate>
        </Stack>
      </Container>

      {/* Upload Dialog */}
      <Dialog
        open={uploadDialogOpen}
        onClose={() => setUploadDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          <Text size="large">Upload Files</Text>
        </DialogTitle>
        <DialogContent>
          <Stack spacing={2} py={2}>
            <input
              type="file"
              multiple
              onChange={handleUpload}
              style={{display: 'none'}}
              id="file-upload-input"
            />
            <label htmlFor="file-upload-input">
              <Button component="span">
                <Text size="body">Choose Files</Text>
              </Button>
            </label>
            <Box sx={{opacity: 0.7}}>
              <Text size="small">Maximum file size: 50 MB</Text>
            </Box>
          </Stack>
        </DialogContent>
      </Dialog>

      {/* Create Folder Dialog */}
      <Dialog
        open={createFolderDialogOpen}
        onClose={() => {
          setCreateFolderDialogOpen(false);
          setFolderName('');
        }}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          <Text size="large">Create Folder</Text>
        </DialogTitle>
        <DialogContent>
          <Stack spacing={2} py={2}>
            <TextField
              label="Folder Name"
              value={folderName}
              onChange={(e) => setFolderName(e.target.value)}
              fullWidth
              variant="filled"
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  handleCreateFolder();
                }
              }}
            />
            <Stack direction="row" spacing={2} justifyContent="flex-end">
              <Button
                onClick={() => {
                  setCreateFolderDialogOpen(false);
                  setFolderName('');
                }}
              >
                <Text size="body">Cancel</Text>
              </Button>
              <Button onClick={handleCreateFolder}>
                <Text size="body">Create</Text>
              </Button>
            </Stack>
          </Stack>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={!!deleteConfirm}
        onClose={() => setDeleteConfirm(null)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          <Text size="large">Delete {deleteConfirm?.type === 'folder' ? 'Folder' : 'File'}</Text>
        </DialogTitle>
        <DialogContent>
          <Stack spacing={2} py={2}>
            <Text size="body">
              Are you sure you want to delete "{deleteConfirm?.name}"? This action cannot be undone.
            </Text>
            <Stack direction="row" spacing={2} justifyContent="flex-end">
              <Button onClick={() => setDeleteConfirm(null)}>
                <Text size="body">Cancel</Text>
              </Button>
              <Button onClick={() => deleteConfirm && handleDelete(deleteConfirm)}>
                <Text size="body">Delete</Text>
              </Button>
            </Stack>
          </Stack>
        </DialogContent>
      </Dialog>
    </Box>
  );
};

export default FileManager;

