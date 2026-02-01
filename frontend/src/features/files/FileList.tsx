import {Box, Grid2} from '@mui/material';
import {FileItem} from './api';
import {FileItemCard} from './FileItemCard';
import Text from '@root/components/Text';
import Button from '@root/components/Button';
import RtkQueryGate from '@root/components/RtkQueryGate';

interface FileListProps {
  files: FileItem[] | undefined;
  isLoading: boolean;
  listError: unknown;
  currentPath: string;
  onFileClick: (file: FileItem) => void;
  onDelete: (file: FileItem) => void;
  onLockToggle: (file: FileItem, lock: boolean) => void;
  onPasswordPrompt: (file: FileItem) => void;
}

export const FileList = ({
  files,
  isLoading,
  listError,
  currentPath,
  onFileClick,
  onDelete,
  onLockToggle,
  onPasswordPrompt,
}: FileListProps) => {
  return (
    <RtkQueryGate checkFetching isLoading={isLoading}>
      {listError && (listError as any)?.data?.locked && (
        <Box textAlign="center" py={4}>
          <Text size="body">This folder is locked</Text>
          <Box mt={2}>
            <Button
              onClick={() => {
                const folderItem: FileItem = {
                  name: currentPath.split('/').pop() || 'Folder',
                  type: 'folder',
                  path: currentPath,
                  locked: true,
                };
                onPasswordPrompt(folderItem);
              }}
            >
              <Text size="body">Enter Password</Text>
            </Button>
          </Box>
        </Box>
      )}
      {!listError && files && files.length === 0 && (
        <Box textAlign="center" py={4}>
          <Text size="body">No files or folders</Text>
        </Box>
      )}
      {!listError && files && files.length > 0 && (
        <Grid2 container spacing={2}>
          {files.map((file) => (
            <Grid2 key={file.path} size={{xs: 6, sm: 4, md: 3}}>
              <FileItemCard
                file={file}
                onFileClick={onFileClick}
                onDelete={onDelete}
                onLockToggle={onLockToggle}
              />
            </Grid2>
          ))}
        </Grid2>
      )}
    </RtkQueryGate>
  );
};

