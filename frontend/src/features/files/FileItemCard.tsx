import {Box, IconButton, Stack} from '@mui/material';
import {FileItem} from './api';
import {FolderIcon, FileIcon, DeleteIcon, LockIcon, UnlockIcon} from './icons';
import {ImageThumbnail} from './ImageThumbnail';
import {formatFileSize, isImageFile} from './utils';
import PillBox from '@root/components/PillBox';
import Text from '@root/components/Text';

interface FileItemCardProps {
  file: FileItem;
  onFileClick: (file: FileItem) => void;
  onDelete: (file: FileItem) => void;
  onLockToggle: (file: FileItem, lock: boolean) => void;
}

export const FileItemCard = ({
  file,
  onFileClick,
  onDelete,
  onLockToggle,
}: FileItemCardProps) => {
  return (
    <PillBox
      sx={{
        p: 2,
        cursor: 'pointer',
        position: 'relative',
        '&:hover': {
          opacity: 0.8,
        },
      }}
      onClick={() => onFileClick(file)}
    >
      <Stack spacing={1} alignItems="center">
        <Box
          sx={{
            width: 48,
            height: 48,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            overflow: 'hidden',
            borderRadius: '4px',
            backgroundColor: 'rgba(255, 255, 255, 0.05)',
          }}
        >
          {file.type === 'folder' ? (
            <FolderIcon width={48} height={48} />
          ) : isImageFile(file.name) ? (
            <ImageThumbnail file={file} />
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
        <Stack
          direction="row"
          spacing={0.5}
          sx={{
            position: 'absolute',
            top: 4,
            right: 4,
          }}
        >
          {file.type === 'folder' && (
            <IconButton
              size="small"
              onClick={(e) => {
                e.stopPropagation();
                onLockToggle(file, !file.locked);
              }}
              sx={{
                color: file.locked ? 'warning.main' : 'text.secondary',
                padding: '4px',
              }}
            >
              {file.locked ? (
                <LockIcon width={16} height={16} />
              ) : (
                <UnlockIcon width={16} height={16} />
              )}
            </IconButton>
          )}
          <IconButton
            size="small"
            onClick={(e) => {
              e.stopPropagation();
              onDelete(file);
            }}
            sx={{
              color: 'error.main',
              padding: '4px',
            }}
          >
            <DeleteIcon width={16} height={16} />
          </IconButton>
        </Stack>
      </Stack>
    </PillBox>
  );
};

