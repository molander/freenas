// Groups Action Creators
// ==================================
// Receive and handle events from the middleware, and call the dispatcher.

"use strict";

import FreeNASDispatcher from "../dispatcher/FreeNASDispatcher";
import { ActionTypes } from "../constants/FreeNASConstants";

class GroupsActionCreators {

  receiveGroupsList ( groupsList ) {
    FreeNASDispatcher.handleMiddlewareAction(
      { type: ActionTypes.RECEIVE_GROUPS_LIST
      , groupsList: groupsList
      }
    );
  }

  receiveGroupUpdateTask ( taskID, groupID ) {
    FreeNASDispatcher.handleMiddlewareAction(
      { type: ActionTypes.RECEIVE_GROUP_UPDATE_TASK
      , taskID: taskID
      , groupID: groupID
      }
    );
  }

};

export default new GroupsActionCreators();