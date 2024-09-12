import './ProfileAvatar.css';

export default function ProfileAvatar(props) {
  const pop_activities_form = (event) => {
    event.preventDefault();
    props.setPopped(true);
    return false;
  }
  const backgroundImage = `url("https://assets.cruddur.myhomelab.xyz/avatars/${props.id}.jpg")`;
  const styles = {
    backgroundImage: backgroundImage,
    backgroundSize: 'cover',
    backgroundPosition: 'center',
  };

  return (
    <div 
        className="profile-avatar"
        style={styles}
        ></div>
  );
}