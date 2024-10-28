def check_errors(model):
  if model['errors'] is not None:
    return model['errors'], 422
  else:
    return model['data'], 200