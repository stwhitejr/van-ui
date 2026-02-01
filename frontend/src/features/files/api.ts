import {createApi, fetchBaseQuery} from '@reduxjs/toolkit/query/react';
import {createBaseUrl} from '@root/util/api';

export const BASE_URL = '/files';

export interface FileItem {
  name: string;
  type: 'file' | 'folder';
  size?: number;
  modified?: string;
  path: string;
  locked?: boolean;
}

export interface UploadFileRequest {
  file: File;
  folder?: string;
}

export interface CreateFolderRequest {
  name: string;
  path?: string;
}

export interface DeleteFileRequest {
  path: string;
}

const filesApi = createApi({
  reducerPath: 'files',
  baseQuery: fetchBaseQuery({
    baseUrl: createBaseUrl(BASE_URL),
  }),
  endpoints: (build) => ({
    listFiles: build.query<FileItem[], string | void>({
      query: (path = '') => ({
        url: `/list`,
        params: path ? {path} : undefined,
      }),
    }),
    uploadFile: build.mutation<{success: boolean; filename: string; path: string}, UploadFileRequest>({
      query: ({file, folder = ''}) => {
        const formData = new FormData();
        formData.append('file', file);
        if (folder) {
          formData.append('folder', folder);
        }
        return {
          url: `/upload`,
          method: 'post',
          body: formData,
        };
      },
    }),
    createFolder: build.mutation<{success: boolean; path: string}, CreateFolderRequest>({
      query: (body) => ({
        url: `/folder`,
        method: 'post',
        body,
      }),
    }),
    deleteFile: build.mutation<{success: boolean}, DeleteFileRequest>({
      query: (body) => ({
        url: `/delete`,
        method: 'delete',
        body,
      }),
    }),
    authenticateFolder: build.mutation<{success: boolean}, {password: string; path: string}>({
      query: (body) => ({
        url: `/authenticate`,
        method: 'post',
        body,
      }),
    }),
    lockFolder: build.mutation<{success: boolean}, {path: string}>({
      query: (body) => ({
        url: `/lock`,
        method: 'post',
        body,
      }),
    }),
    unlockFolder: build.mutation<{success: boolean}, {path: string}>({
      query: (body) => ({
        url: `/unlock`,
        method: 'post',
        body,
      }),
    }),
  }),
});

export default filesApi;

export const {
  useListFilesQuery,
  useUploadFileMutation,
  useCreateFolderMutation,
  useDeleteFileMutation,
  useAuthenticateFolderMutation,
  useLockFolderMutation,
  useUnlockFolderMutation,
} = filesApi;

