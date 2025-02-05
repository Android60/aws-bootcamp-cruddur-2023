import './ProfileForm.css';
import React from "react";
import process from 'process';
import {getAccessToken} from 'lib/CheckAuth';

export default function ProfileForm(props) {
  const [bio, setBio] = React.useState('');
  const [displayName, setDisplayName] = React.useState('');

  React.useEffect(()=>{
    if (props.profile.bio === null)
      setBio('');
    else
      setBio(props.profile.bio);
    setDisplayName(props.profile.display_name);
  }, [props.profile])

  const s3upload = async (event)=> {
    event.preventDefault();
    const file = event.target.files[0]
    const filename = file.name
    const type = file.type
    const preview_image_url = URL.createObjectURL(file)
    console.log("file",file)
    const fileparts = filename.split('.')
    const extension = fileparts[fileparts.length-1]
    let presignedUrl = await s3uploadkey(extension)

    console.log(presignedUrl)
    try {
      const res = await fetch(presignedUrl, {
        method: "PUT",
        body: file,
        headers: {
          'Origin': `${process.env.REACT_APP_FRONTEND_URL}`,
          'Accept': 'application/json',
          'Content-Type': type
        }
      });
      if (res.status === 200) {
        console.log('File uploaded')
      } else {
        console.log(res)
      }
    } catch (err) {
      console.log(err);
    }
  }

  const s3uploadkey = async (extension)=> {
    try {
      const api_gw = `${process.env.REACT_APP_API_GATEWAY_URL}/avatars/key_upload`
      await getAccessToken()
      const access_token = localStorage.getItem("access_token")
      const json = {
        extension: extension
      }
      const res = await fetch(api_gw, {
        method: "POST",
        body: JSON.stringify(json),
        headers: {
          'Origin': `${process.env.REACT_APP_FRONTEND_URL}`,
          'Authorization': `Bearer ${access_token}`,
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      });
      let data = await res.json();
      if (res.status === 200) {
        console.log('presigned url', data)
        return data.url
      } else {
        console.log(res)
      }
    } catch (err) {
      console.log(err);
    }
  }

  const onsubmit = async (event) => {
    event.preventDefault();
    try {
      const backend_url = `${process.env.REACT_APP_BACKEND_URL}/api/profile/update`
      await getAccessToken()
      const access_token = localStorage.getItem("access_token")
      const res = await fetch(backend_url, {
        method: "POST",
        headers: {
          'Authorization': `Bearer ${access_token}`,
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          bio: bio,
          display_name: displayName
        }),
      });
      let data = await res.json();
      if (res.status === 200) {
        setBio(null)
        setDisplayName(null)
        props.setPopped(false)
      } else {
        console.log(res)
      }
    } catch (err) {
      console.log(err);
    }
  }

  const bio_onchange = (event) => {
    setBio(event.target.value);
  }

  const display_name_onchange = (event) => {
    setDisplayName(event.target.value);
  }

  const close = (event)=> {
    console.log('close',event.target)
    if (event.target.classList.contains("profile_popup")) {
      props.setPopped(false)
    }
  }

  if (props.popped === true) {
    return (
      <div className="popup_form_wrap profile_popup" onClick={close}>
        <form 
          className='profile_form popup_form'
          onSubmit={onsubmit}
        >
          <div className="popup_heading">
            <div className="popup_title">Edit Profile</div>
            <div className='submit'>
              <button type='submit'>Save</button>
            </div>
          </div>
          <div className="popup_content">
            {/* <div className="upload" onClick={s3uploadkey}>
              Upload Avatar
            </div> */}
            <input type="file" name="avatarupload" onChange={s3upload} accept="image/png, image/jpeg"/>
            <div className="field display_name">
              <label>Display Name</label>
              <input
                type="text"
                placeholder="Display Name"
                value={displayName}
                onChange={display_name_onchange} 
              />
            </div>
            <div className="field bio">
              <label>Bio</label>
              <textarea
                placeholder="Bio"
                value={bio}
                onChange={bio_onchange} 
              />
            </div>
          </div>
        </form>
      </div>
    );
  }
}