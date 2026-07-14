from complete_dfd_builder import flows_data
processes = set()
for f_name, connections in flows_data.items():
  for src, dst in connections:
    if src.startswith('Process'): processes.add(src)
    if dst.startswith('Process'): processes.add(dst)
print(sorted(list(processes)))
