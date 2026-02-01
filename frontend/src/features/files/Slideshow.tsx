import {Box, IconButton} from '@mui/material';
import {useEffect} from 'react';
import {FileItem} from './api';
import {createBaseUrl} from '@root/util/api';
import {CloseIcon} from './icons';

const BASE_URL = '/files';

interface SlideshowProps {
  open: boolean;
  images: FileItem[];
  currentIndex: number;
  onClose: () => void;
  onIndexChange: (index: number) => void;
}

export const Slideshow = ({
  open,
  images,
  currentIndex,
  onClose,
  onIndexChange,
}: SlideshowProps) => {
  useEffect(() => {
    if (!open || images.length === 0) {
      return;
    }

    const interval = setInterval(() => {
      onIndexChange((currentIndex + 1) % images.length);
    }, 5000);

    return () => clearInterval(interval);
  }, [open, images.length, currentIndex, onIndexChange]);

  if (!open || images.length === 0) {
    return null;
  }

  const currentImage = images[currentIndex];
  const imageUrl = `${createBaseUrl(BASE_URL)}/view/${currentImage.path
    .split('/')
    .map((segment) => encodeURIComponent(segment))
    .join('/')}`;

  return (
    <Box
      sx={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.95)',
        zIndex: 9999,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      <Box
        sx={{
          position: 'relative',
          width: '100%',
          height: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <Box
          component="img"
          src={imageUrl}
          alt={currentImage.name}
          sx={{
            maxWidth: '100%',
            maxHeight: '100%',
            objectFit: 'contain',
          }}
          onError={() => {
            // Skip to next image if current one fails to load
            setTimeout(() => {
              onIndexChange((currentIndex + 1) % images.length);
            }, 100);
          }}
        />
        <IconButton
          onClick={onClose}
          sx={{
            position: 'absolute',
            top: 16,
            right: 16,
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            color: 'white',
            '&:hover': {
              backgroundColor: 'rgba(0, 0, 0, 0.7)',
            },
          }}
        >
          <CloseIcon width={24} height={24} />
        </IconButton>
      </Box>
    </Box>
  );
};

