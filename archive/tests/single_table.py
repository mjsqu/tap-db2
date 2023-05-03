import sys

def select_stream_from_catalog(catalog_file,tap_stream_id):
    import json
    with open(catalog_file,'r') as f:
        catalog = json.load(f)
    
    streams = catalog.get('streams')
    selected_stream = [stream for stream in streams if stream.get('tap_stream_id') == tap_stream_id]
    new_catalog = {"streams":selected_stream}
    return json.dumps(new_catalog)

stream = select_stream_from_catalog("../catalog.json",f"DB2INST1-{sys.argv[1].upper()}")
with open(f"../{sys.argv[1]}.json",'w') as f:
    f.write(stream)