import './ActivityFeed.css';
import ActivityItem from './ActivityItem';

export default function ActivityFeed(props) {
  if (props.loading === true){
    return (
        <div className='loader'></div>
    )
  }
  else {
    if (props.activities.length === 0){
      return (
      <div className='activity_feed_primer'>
        <span>It's so empty!</span>
      </div>
      );
    } else {
    return (
      <div className='activity_feed_collection'>
        {props.activities.map(activity => {
        return  <ActivityItem setReplyActivity={props.setReplyActivity} setPopped={props.setPopped} key={activity.uuid} activity={activity} />
        })}
      </div>
    );}
  }
}