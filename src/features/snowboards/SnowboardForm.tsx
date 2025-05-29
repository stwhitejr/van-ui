import {Field, FieldProps, Formik} from 'formik';
import {Snowboard} from './types';
import * as Yup from 'yup';
import {SnowboardTypes} from './constants';
import {
  Button,
  FormControl,
  Grid2 as Grid,
  InputLabel,
  MenuItem,
  Select,
  TextField,
} from '@mui/material';

const FormikTextField = ({field, form, ...rest}: FieldProps) => {
  const error = form.errors[field.name];
  const isTouched = form.touched[field.name];
  return (
    <TextField
      fullWidth
      {...field}
      {...rest}
      error={isTouched && !!error}
      helperText={isTouched && (error as string)}
    />
  );
};

const SnowboardTypesDropdown = ({
  field,
  form,
  ...rest
}: FieldProps<{label: string}>) => {
  const error = form.errors[field.name];
  const isTouched = form.touched[field.name];

  return (
    <FormControl fullWidth>
      <InputLabel>{rest.label}</InputLabel>
      <Select fullWidth {...field} {...rest} error={isTouched && !!error}>
        {SnowboardTypes.map((type) => (
          <MenuItem key={type} value={type}>
            {type}
          </MenuItem>
        ))}
      </Select>
    </FormControl>
  );
};

export interface SnowboardFormProps {
  value?: Snowboard;
  onSubmit?: (arg: Snowboard) => void;
}

const SnowboardStartingValue: PropsNullable<Snowboard> = {
  id: null,
  type: null,
  brand: null,
  model: null,
  length: null,
};

const SnowboardForm = ({onSubmit, value}: SnowboardFormProps) => {
  return (
    <Formik<Snowboard>
      initialValues={value || SnowboardStartingValue}
      onSubmit={(values) => {
        onSubmit?.(values);
      }}
      validationSchema={Yup.object({
        brand: Yup.string().required('Required'),
        model: Yup.string().required('Required'),
        length: Yup.number().required('Required').min(100, 'Size too small'),
        type: Yup.mixed()
          .required('Required')
          .oneOf(SnowboardTypes, `Must be one of ${SnowboardTypes.join(', ')}`),
      })}
    >
      {({values, handleSubmit, isValid}) => (
        <Grid container spacing={2}>
          <Grid size={6}>
            <Field
              component={FormikTextField}
              value={values.brand}
              type="string"
              label="Brand"
              name="brand"
            />
          </Grid>
          <Grid size={6}>
            <Field
              component={FormikTextField}
              value={values.model}
              type="string"
              label="Model"
              name="model"
            />
          </Grid>
          <Grid size={6}>
            <Field
              component={FormikTextField}
              value={values.length}
              type="number"
              label="Length"
              name="length"
            />
          </Grid>
          <Grid size={6}>
            <Field
              component={SnowboardTypesDropdown}
              value={values.type}
              type="string"
              label="Type"
              name="type"
            />
          </Grid>
          {onSubmit && (
            <Grid size={12}>
              <Button disabled={!isValid} onClick={() => handleSubmit()}>
                Submit
              </Button>
            </Grid>
          )}
        </Grid>
      )}
    </Formik>
  );
};

export default SnowboardForm;
