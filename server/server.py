from pyVmomi import vim
from pyVim.connect import SmartConnectNoSSL, Disconnect
from flask import Flask, jsonify, request
app = Flask(__name__)


class Connection:
    def __enter__(self):
        host = request.args.get('server')
        user = request.args.get('user')
        pwd = request.args.get('pass')
        si = SmartConnectNoSSL(host=host, user=user, pwd=pwd)
        self._si = si
        return si

    def __exit__(self, type, value, traceback):
        Disconnect(self._si)


def get_all(content, vimtype, recursive=True):
    objView = content.viewManager.CreateContainerView(
        content.rootFolder, vimtype, recursive)
    objs = objView.view
    objView.Destroy()
    return objs


def get_obj(content, vimtype, name):
    objs = get_all(content, vimtype)
    if name is None:
        return objs[0]

        for obj in objs:
            if obj.name == name:
                return obj


@app.route('/api/machine:clone', methods=['GET'])
def create_task():
    name = request.args.get('name')
    source = request.args.get('source')
    folder = request.args.get('folder')
    host = request.args.get('host')
    pool = request.args.get('pool')
    datastore = request.args.get('datastore')

    with Connection() as si:
        # content = si.content
        search_index = si.content.searchIndex
        vm = search_index.FindByInventoryPath(source)
        folder = search_index.FindByInventoryPath(folder)
        datastore = search_index.FindByInventoryPath(datastore)
        host = search_index.FindByInventoryPath(host)
        pool = search_index.FindByInventoryPath(pool)

        relspec = vim.vm.RelocateSpec()
        relspec.datastore = datastore
        relspec.host = host
        relspec.pool = pool

        clonespec = vim.vm.CloneSpec()
        clonespec.location = relspec

        vm.Clone(folder=folder, name=name, spec=clonespec)
        print('Cloning')
        return jsonify({'success': True})


if __name__ == '__main__':
    app.run(debug=True)
