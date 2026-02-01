import {Box, Dialog, DialogContent, DialogTitle, Stack} from '@mui/material';
import {ChangeEvent} from 'react';
import Button from '@root/components/Button';
import Text from '@root/components/Text';

interface UploadDialogProps {
  open: boolean;
  onClose: () => void;
  onUpload: (event: ChangeEvent<HTMLInputElement>) => void;
}

export const UploadDialog = ({open, onClose, onUpload}: UploadDialogProps) => {
  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        <Text size="large">Upload Files</Text>
      </DialogTitle>
      <DialogContent>
        <Stack spacing={2} py={2}>
          <input
            type="file"
            multiple
            onChange={onUpload}
            style={{display: 'none'}}
            id="file-upload-input"
          />
          <Box
            component="label"
            htmlFor="file-upload-input"
            sx={{cursor: 'pointer', display: 'inline-block'}}
          >
            <Button onClick={() => {}}>
              <Text size="body">Choose Files</Text>
            </Button>
          </Box>
          <Box sx={{opacity: 0.7}}>
            <Text size="small">Maximum file size: 50 MB</Text>
          </Box>
        </Stack>
      </DialogContent>
    </Dialog>
  );
};

