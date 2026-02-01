import {Dialog, DialogContent, DialogTitle, Stack} from '@mui/material';
import Button from '@root/components/Button';
import Text from '@root/components/Text';
import {FileItem} from './api';

interface DeleteConfirmDialogProps {
  file: FileItem | null;
  onClose: () => void;
  onConfirm: () => void;
}

export const DeleteConfirmDialog = ({
  file,
  onClose,
  onConfirm,
}: DeleteConfirmDialogProps) => {
  if (!file) {
    return null;
  }

  return (
    <Dialog open={!!file} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        <Text size="large">Delete {file.type === 'folder' ? 'Folder' : 'File'}</Text>
      </DialogTitle>
      <DialogContent>
        <Stack spacing={2} py={2}>
          <Text size="body">
            Are you sure you want to delete "{file.name}"? This action cannot be undone.
          </Text>
          <Stack direction="row" spacing={2} justifyContent="flex-end">
            <Button onClick={onClose}>
              <Text size="body">Cancel</Text>
            </Button>
            <Button onClick={onConfirm}>
              <Text size="body">Delete</Text>
            </Button>
          </Stack>
        </Stack>
      </DialogContent>
    </Dialog>
  );
};

