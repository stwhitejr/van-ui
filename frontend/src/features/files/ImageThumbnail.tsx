import {Box} from '@mui/material';
import {useState} from 'react';
import {FileIcon} from './icons';
import {FileItem} from './api';
import {createBaseUrl} from '@root/util/api';

const BASE_URL = '/files';

interface ImageThumbnailProps {
  file: FileItem;
}

export const ImageThumbnail = ({file}: ImageThumbnailProps) => {
  const [imageError, setImageError] = useState(false);
  const imageUrl = `${createBaseUrl(BASE_URL)}/view/${file.path
    .split('/')
    .map((segment) => encodeURIComponent(segment))
    .join('/')}`;

  if (imageError) {
    return <FileIcon width={48} height={48} />;
  }

  return (
    <Box
      component="img"
      src={imageUrl}
      alt={file.name}
      onError={() => setImageError(true)}
      sx={{
        width: '100%',
        height: '100%',
        objectFit: 'cover',
      }}
    />
  );
};

