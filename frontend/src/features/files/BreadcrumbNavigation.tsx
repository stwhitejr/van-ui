import {Breadcrumbs, Link} from '@mui/material';

interface BreadcrumbNavigationProps {
  paths: string[];
  onNavigate: (index: number) => void;
}

export const BreadcrumbNavigation = ({
  paths,
  onNavigate,
}: BreadcrumbNavigationProps) => {
  return (
    <Breadcrumbs>
      {paths.map((part, index) => (
        <Link
          key={index}
          component="button"
          variant="body1"
          onClick={() => onNavigate(index)}
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
  );
};

