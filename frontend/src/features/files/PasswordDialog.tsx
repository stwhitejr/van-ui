import {Dialog, DialogContent, DialogTitle, Stack, TextField} from '@mui/material';
import {KeyboardEvent} from 'react';
import Button from '@root/components/Button';
import Text from '@root/components/Text';
import {FileItem} from './api';

interface PasswordDialogProps {
  open: boolean;
  password: string;
  folder: FileItem | null;
  onClose: () => void;
  onPasswordChange: (password: string) => void;
  onSubmit: () => void;
}

export const PasswordDialog = ({
  open,
  password,
  folder,
  onClose,
  onPasswordChange,
  onSubmit,
}: PasswordDialogProps) => {
  const handleKeyPress = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      onSubmit();
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        <Text size="large">Enter Password</Text>
      </DialogTitle>
      <DialogContent>
        <Stack spacing={2} py={2}>
          <Text size="body">
            The folder "{folder?.name}" is locked. Please enter the password to access it.
          </Text>
          <TextField
            label="Password"
            type="password"
            value={password}
            onChange={(e) => onPasswordChange(e.target.value)}
            fullWidth
            variant="filled"
            onKeyPress={handleKeyPress}
          />
          <Stack direction="row" spacing={2} justifyContent="flex-end">
            <Button onClick={onClose}>
              <Text size="body">Cancel</Text>
            </Button>
            <Button onClick={onSubmit}>
              <Text size="body">Submit</Text>
            </Button>
          </Stack>
        </Stack>
      </DialogContent>
    </Dialog>
  );
};

