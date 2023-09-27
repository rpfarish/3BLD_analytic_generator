# # Create drill file for comm trainer
#
# for buffer in buffer_order['corners']:
#     with open(r"C:\Users\rpfar\Documents\jashaszun-3style-tester\
#     jashaszun-3style-tester-0980b6fbd87e\Comms\Floating Corners{}.txt".format(buffer), 'w') as f:
#         all_corners = convert_letterpairs(Drill().get_all_buffer_targets(buffer, 'corners'),
#         'loc_to_letters', 'corners')
#         all_corners = [corner + "=\n" for corner in all_corners]
#         corner_str = "".join(all_corners)
#         f.writelines(all_corners)
# for buffer in buffer_order['edges']:
#     with open(r"C:\Users\rpfar\Documents\jashaszun-3style-tester\jashaszun-3style-tester-0980b6fbd87e
#     \Comms\Floating Edges\{}.txt".format(buffer), 'w') as f:
#         all_edges = convert_letterpairs(Drill().get_all_buffer_targets(buffer, 'edges'), 'loc_to_letters', 'edges')
#         all_edges = [edge + "=\n" for edge in all_edges]
#         edge_str = "".join(all_edges)
#         f.writelines(all_edges)
