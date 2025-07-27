export interface Edit{
  measurement: string,
  simulated: boolean,
  runs_on: string,
  name: string,
  value: string,
  field: string,
  bucket: string,
  update_front: boolean,
  datetime: string,
  axis: string | undefined
}
