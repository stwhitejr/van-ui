import SnowboardForm from '@root/features/snowboards/SnowboardForm';
import useGetSnowboard from '@root/features/snowboards/useGetSnowboard';
import {snowboardsPath} from '@root/paths';
import {Navigate, useNavigate, useParams} from 'react-router-dom';
import useToast from '@root/features/toast/useToast';

const SnowboardUpdatePage = () => {
  const {id} = useParams();
  const navigate = useNavigate();
  const setToast = useToast();

  const snowboard = useGetSnowboard(id);

  const handleSubmit = (values) => {
    // This is where you hit the update API or update redux if we use a local draft
    console.log(values);
    setToast({status: 'success', message: 'Updated!'});
    navigate(snowboardsPath({}));
  };
  if (!id) {
    return <Navigate to={snowboardsPath({})} />;
  }
  return <SnowboardForm value={snowboard} onSubmit={handleSubmit} />;
};

export default SnowboardUpdatePage;
