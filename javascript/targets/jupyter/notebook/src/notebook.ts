import { RemoteClip } from '@yuuno2/remote';
import { ClipViewer } from '@yuuno2/jupyter-ui';
import { WidgetConnection } from '@yuuno2/jupyter-networking'

export function load_ipython_extension() {
    console.log("Loading Yuuno2 for Jupyter Notebook");
}

export { RemoteClip, ClipViewer, WidgetConnection };