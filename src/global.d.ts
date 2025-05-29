export {};

declare global {
  type ValueOf<T> = T[keyof T];
  type PropsNullable<T> = {[K in keyof T]: T[K] | null};
  type PropsListable<T> = {[K in keyof T]: T[K] | T[K][]};
}
