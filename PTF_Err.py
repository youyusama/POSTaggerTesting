from global_variables import *


class PTF_Err():
	def __init__(self, key, key_id, ori_pos, mut_pos):
		self.key = key
		self.id = key_id
		self.ori_pos = ori_pos
		self.mut_pos = mut_pos


def create_error_map(error_map):
	for key in UPOS_TAG_LIST:
		error_map[key]={}
		for key2 in UPOS_TAG_LIST:
			error_map[key][key2]={}


def accumulate_error_by_res(error_map, res, ori_sen_doc, mut_sen_doc):
	error_num = 0
	# at least i understand it right now
	for error_i in res:
		if (error_i.ori_pos, error_i.mut_pos) in UNWANTED_ERRORS[1]:
			continue
		if (error_i.ori_pos, error_i.mut_pos) in UNWANTED_ERRORS[0] and ( error_i.key.endswith('ed') or error_i.key.endswith('ing') ):
			continue
		key_and_id = error_i.key + ' ' + str(error_i.id)
		if ori_sen_doc in error_map[error_i.ori_pos][error_i.mut_pos]:
			if key_and_id in error_map[error_i.ori_pos][error_i.mut_pos][ori_sen_doc]:
				error_map[error_i.ori_pos][error_i.mut_pos][ori_sen_doc][key_and_id].append(mut_sen_doc)
			else:
				error_map[error_i.ori_pos][error_i.mut_pos][ori_sen_doc][key_and_id] = [mut_sen_doc]
		else:
			error_map[error_i.ori_pos][error_i.mut_pos][ori_sen_doc] = {key_and_id: [mut_sen_doc]}
		error_num += 1
	return error_num