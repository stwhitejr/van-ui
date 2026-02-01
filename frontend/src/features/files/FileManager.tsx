import {Box, Stack} from '@mui/material';
import {useState, useCallback, useMemo} from 'react';
import {ChangeEvent} from 'react';
import Button from '@root/components/Button';
import Text from '@root/components/Text';
import Container from '@root/components/Container';
import {
  useListFilesQuery,
  useUploadFileMutation,
  useCreateFolderMutation,
  useDeleteFileMutation,
  useAuthenticateFolderMutation,
  useLockFolderMutation,
  useUnlockFolderMutation,
  FileItem,
} from './api';
import {createBaseUrl} from '@root/util/api';
import useToast from '@root/features/toast/useToast';
import {isImageFile} from './utils';
import {BreadcrumbNavigation} from './BreadcrumbNavigation';
import {FileList} from './FileList';
import {UploadDialog} from './UploadDialog';
import {CreateFolderDialog} from './CreateFolderDialog';
import {PasswordDialog} from './PasswordDialog';
import {DeleteConfirmDialog} from './DeleteConfirmDialog';
import {Slideshow} from './Slideshow';

const BASE_URL = '/files';

const FileManager = () => {
  const [currentPath, setCurrentPath] = useState<string>('');
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [createFolderDialogOpen, setCreateFolderDialogOpen] = useState(false);
  const [folderName, setFolderName] = useState('');
  const [deleteConfirm, setDeleteConfirm] = useState<FileItem | null>(null);
  const [passwordDialogOpen, setPasswordDialogOpen] = useState(false);
  const [password, setPassword] = useState('');
  const [lockedFolderToAccess, setLockedFolderToAccess] = useState<FileItem | null>(null);
  const [slideshowOpen, setSlideshowOpen] = useState(false);
  const [currentSlideIndex, setCurrentSlideIndex] = useState(0);
  const toast = useToast();

  const {
    data: files,
    isLoading,
    error: listError,
    refetch,
  } = useListFilesQuery(currentPath || undefined);

  const [uploadFile] = useUploadFileMutation();
  const [createFolder] = useCreateFolderMutation();
  const [deleteFile] = useDeleteFileMutation();
  const [authenticateFolder] = useAuthenticateFolderMutation();
  const [lockFolder] = useLockFolderMutation();
  const [unlockFolder] = useUnlockFolderMutation();

  const handleNavigate = useCallback((path: string) => {
    setCurrentPath(path);
  }, []);

  const handleFileClick = useCallback(
    (file: FileItem) => {
      if (file.type === 'folder') {
        if (file.locked) {
          setLockedFolderToAccess(file);
          setPasswordDialogOpen(true);
        } else {
          handleNavigate(file.path);
        }
      } else {
        const pathSegments = file.path.split('/').map((segment) => encodeURIComponent(segment));
        const encodedPath = pathSegments.join('/');
        const url = `${createBaseUrl(BASE_URL)}/view/${encodedPath}`;
        window.open(url, '_blank');
      }
    },
    [handleNavigate]
  );

  const handlePasswordSubmit = useCallback(async () => {
    if (!lockedFolderToAccess || !password.trim()) {
      toast({message: 'Please enter a password', status: 'error'});
      return;
    }

    try {
      await authenticateFolder({
        password: password.trim(),
        path: lockedFolderToAccess.path,
      }).unwrap();
      toast({message: 'Access granted', status: 'success'});
      setPasswordDialogOpen(false);
      setPassword('');
      setLockedFolderToAccess(null);
      handleNavigate(lockedFolderToAccess.path);
      refetch();
    } catch (error: any) {
      toast({
        message: error?.data?.error || 'Incorrect password',
        status: 'error',
      });
      setPassword('');
    }
  }, [lockedFolderToAccess, password, authenticateFolder, toast, handleNavigate, refetch]);

  const handleLockToggle = useCallback(
    async (file: FileItem, lock: boolean) => {
      try {
        if (lock) {
          await lockFolder({path: file.path}).unwrap();
          toast({message: 'Folder locked', status: 'success'});
        } else {
          await unlockFolder({path: file.path}).unwrap();
          toast({message: 'Folder unlocked', status: 'success'});
        }
        refetch();
      } catch (error: any) {
        toast({
          message: error?.data?.error || `Failed to ${lock ? 'lock' : 'unlock'} folder`,
          status: 'error',
        });
      }
    },
    [lockFolder, unlockFolder, toast, refetch]
  );

  const handleUpload = useCallback(
    async (event: ChangeEvent<HTMLInputElement>) => {
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

  const breadcrumbPaths = useMemo(
    () => (currentPath ? ['', ...currentPath.split('/')] : ['']),
    [currentPath]
  );

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

  const imageFiles = useMemo(
    () => files?.filter((file) => file.type === 'file' && isImageFile(file.name)) || [],
    [files]
  );

  const handleStartSlideshow = useCallback(() => {
    if (imageFiles.length === 0) {
      toast({message: 'No images in this folder', status: 'error'});
      return;
    }
    setCurrentSlideIndex(0);
    setSlideshowOpen(true);
  }, [imageFiles.length, toast]);

  const handlePasswordPrompt = useCallback((file: FileItem) => {
    setLockedFolderToAccess(file);
    setPasswordDialogOpen(true);
  }, []);

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
            <Button onClick={handleStartSlideshow}>
              <Text size="body">Slideshow</Text>
            </Button>
          </Stack>
        }
      >
        <Stack spacing={2}>
          <BreadcrumbNavigation paths={breadcrumbPaths} onNavigate={handleBreadcrumbClick} />

          <FileList
            files={files}
            isLoading={isLoading}
            listError={listError}
            currentPath={currentPath}
            onFileClick={handleFileClick}
            onDelete={setDeleteConfirm}
            onLockToggle={handleLockToggle}
            onPasswordPrompt={handlePasswordPrompt}
          />
        </Stack>
      </Container>

      <UploadDialog
        open={uploadDialogOpen}
        onClose={() => setUploadDialogOpen(false)}
        onUpload={handleUpload}
      />

      <CreateFolderDialog
        open={createFolderDialogOpen}
        folderName={folderName}
        onClose={() => {
          setCreateFolderDialogOpen(false);
          setFolderName('');
        }}
        onFolderNameChange={setFolderName}
        onCreate={handleCreateFolder}
      />

      <PasswordDialog
        open={passwordDialogOpen}
        password={password}
        folder={lockedFolderToAccess}
        onClose={() => {
          setPasswordDialogOpen(false);
          setPassword('');
          setLockedFolderToAccess(null);
        }}
        onPasswordChange={setPassword}
        onSubmit={handlePasswordSubmit}
      />

      <Slideshow
        open={slideshowOpen}
        images={imageFiles}
        currentIndex={currentSlideIndex}
        onClose={() => {
          setSlideshowOpen(false);
          setCurrentSlideIndex(0);
        }}
        onIndexChange={setCurrentSlideIndex}
      />

      <DeleteConfirmDialog
        file={deleteConfirm}
        onClose={() => setDeleteConfirm(null)}
        onConfirm={() => deleteConfirm && handleDelete(deleteConfirm)}
      />
    </Box>
  );
};

export default FileManager;
