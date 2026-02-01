import {Dialog, DialogContent, DialogTitle, Stack, TextField} from '@mui/material';
import {KeyboardEvent} from 'react';
import Button from '@root/components/Button';
import Text from '@root/components/Text';

interface CreateFolderDialogProps {
  open: boolean;
  folderName: string;
  onClose: () => void;
  onFolderNameChange: (name: string) => void;
  onCreate: () => void;
}

export const CreateFolderDialog = ({
  open,
  folderName,
  onClose,
  onFolderNameChange,
  onCreate,
}: CreateFolderDialogProps) => {
  const handleKeyPress = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      onCreate();
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        <Text size="large">Create Folder</Text>
      </DialogTitle>
      <DialogContent>
        <Stack spacing={2} py={2}>
          <TextField
            label="Folder Name"
            value={folderName}
            onChange={(e) => onFolderNameChange(e.target.value)}
            fullWidth
            variant="filled"
            onKeyPress={handleKeyPress}
          />
          <Stack direction="row" spacing={2} justifyContent="flex-end">
            <Button onClick={onClose}>
              <Text size="body">Cancel</Text>
            </Button>
            <Button onClick={onCreate}>
              <Text size="body">Create</Text>
            </Button>
          </Stack>
        </Stack>
      </DialogContent>
    </Dialog>
  );
};

