import os
import sys
import re
import string

try:
    from Bio.WWW import NCBI
except ImportError:
    pass
else:
    from Bio.Blast import NCBIWWW
    from Bio import Fasta
    from Bio.Clustalw import MultipleAlignCL
    import Bio.Clustalw

import global_functions

def Sequence_Through_Clustalw( sequence, system, chain=None):
    """ do the entire sequence """
    b_tag = system.get_filename_by_extension('.fst', chain)
    cwin_tag = system.get_filename_by_extension('.cin', chain)
    dos_cwin_tag = global_functions.translate_filename_to_DOS_8_3_format(cwin_tag)
    cwout_tag = system.get_filename_by_extension('.clu', chain)
    dos_cwout_tag = global_functions.translate_filename_to_DOS_8_3_format(cwout_tag)
    cwaligned_tag = system.get_filename_by_extension('.aln', chain)
    print 'cwaligned_tag = %s'%(cwaligned_tag)
    dos_cwaligned_tag = global_functions.translate_filename_to_DOS_8_3_format(cwaligned_tag)
    #the cwprot_tag can only differ from the tag given to Clustalw_Protein by its extension
    print "BLASTing %s\n"%(sequence)
    Blastp_( sequence, b_tag )
    print "BLAST Complete, Fetching Sequences\n"
    Create_Clustalw_Input( sequence, b_tag, dos_cwin_tag, 'ON')
    print "Fetch Complete, Clustalw Aligned Sequences\n"
    Clustalw_Align( dos_cwin_tag, dos_cwout_tag )
    print "Matching Fasta headers to alignments\n"
    Bridge_Fasta_Header_And_Aligned( dos_cwin_tag, dos_cwout_tag, dos_cwaligned_tag )
    return cwaligned_tag

def Resequence_From_FST( sequence, system, chain=None):
    """ do the entire sequence """
    b_tag = system.get_filename_by_extension('.fst', chain)
    cwin_tag = system.get_filename_by_extension('.cin', chain)
    dos_cwin_tag = global_functions.translate_filename_to_DOS_8_3_format(cwin_tag)
    cwout_tag = system.get_filename_by_extension('.clu', chain)
    dos_cwout_tag = global_functions.translate_filename_to_DOS_8_3_format(cwout_tag)
    cwaligned_tag = system.get_filename_by_extension('.aln', chain)
    print 'sequencing from FST'
    dos_cwaligned_tag = global_functions.translate_filename_to_DOS_8_3_format(cwaligned_tag)
    #the cwprot_tag can only differ from the tag given to Clustalw_Protein by its extension
    #print "BLASTing %s\n"%(sequence)
    #Blastp_( sequence, b_tag )
    print "BLAST Complete, Fetching Sequences\n"
    Create_Clustalw_Input( sequence, b_tag, dos_cwin_tag, 'ON')
    print "aligning with clustalW\n"
    Clustalw_Align( dos_cwin_tag, dos_cwout_tag )
    print "matching fasta headers to alignments\n"
    Bridge_Fasta_Header_And_Aligned( dos_cwin_tag, dos_cwout_tag, dos_cwaligned_tag )
    return cwaligned_tag

def Resequence_From_CIN(sequence, system, chain=None):
    cwin_tag = system.get_filename_by_extension('.cin', chain)
    dos_cwin_tag = global_functions.translate_filename_to_DOS_8_3_format(cwin_tag)
    cwout_tag = system.get_filename_by_extension('.clu', chain)
    dos_cwout_tag = global_functions.translate_filename_to_DOS_8_3_format(cwout_tag)
    cwaligned_tag = system.get_filename_by_extension('.aln', chain)
    dos_cwaligned_tag = global_functions.translate_filename_to_DOS_8_3_format(cwaligned_tag)
    #the cwprot_tag can only differ from the tag given to Clustalw_Protein by its extension
    print 'sequencer from CIN'
    print 'aligning with clustalW'
    Clustalw_Align( dos_cwin_tag, dos_cwout_tag )
    print "matching fasta headers to alignments\n"
    Bridge_Fasta_Header_And_Aligned( dos_cwin_tag, dos_cwout_tag, dos_cwaligned_tag )
    return cwaligned_tag

def Blastp_( fasta_sequence, out_file = 'Blastp.txt', format = 'Text'):
    """ Purpose: Retrieve BLAST(blastp) information of 'fasta_sequence' and store
        it to a file
    """
    b_result = NCBIWWW.blast( 'blastp', 'nr', fasta_sequence, format_type = format )
    save_file = open( out_file, 'w' )
    save_file.write( b_result.read() )
    save_file.close()

def Create_Clustalw_Input( sequence, blast_file = 'Blastp.txt', out_file = 'CWIn.txt',repeat_filter = 'ON'):
    """ Purpose: Take output of Retrieve_Blastp and create a Clustalw input file
        'filter' acts as a gate for doing only one sequence for a title
        returns a list of the titles done in the order they were appended
    """
    # first advance the reader to the beginning of the accession # (gi...) headers
    results_file = Advance_Reader( blast_file )
    if( results_file == 0 ):
        return

    Begin_Clustalw_File(sequence, out_file)    
    titles_done = []    #a list of the stored titles
    total_count = 1;    #a counter that tells how many sequences have been decided
    #read in a sequence, see if a sequence with the same title has been seen already,
    #if seen, skip, else append name to titles_done and fetch entire sequence from NCBI
    sequence_header = results_file.readline()
    while( sequence_header != '\n' ):
        space = sequence_header.find(' ') + 1 #get title
        title = sequence_header[ space:67 ]
        if not title in titles_done or repeat_filter != 'ON':    #this filters out repeated titles
            # I wanted to reduce the number of repeating sequences
            titles_done.append( title )
            gi, pid, gb = sequence_header.split( "|", 2 )  #get gi
            print 'appending %s to %s add %s'%(pid, out_file, gb)
            Append_Unique_Protein_Fasta( pid, out_file, 'Text' )
        total_count = total_count+1
        if(total_count == 50):
            break
        sequence_header = results_file.readline()
    return titles_done

def Advance_Reader( blast_file ):
    """ Advance the reader of a file to the line 'Sequences producing significant alignments:'
        and return it
    """
    results_file = open( blast_file, 'r' )
    #read in lines from the blast_file until a line contains what the match_line holds
    #this marks the beginning of the list of sequences
    to_find = '.*Sequences producing significant alignments:.*'
    match_line = re.compile( to_find )
    read_line = results_file.readline()
    while( read_line != "" ):
        if( match_line.match( read_line ) ):
            break
        read_line = results_file.readline()
    if( read_line == "" ):
        print "'"+to_find+"' could not be find in file: " + blast_file
        results_file.close()
        results_file = open(blast_file, 'r')
        return  results_file #end of file reached
    results_file.readline()
    return results_file

def Clustalw_Align(input_file = 'CWIn.txt', output_file = 'CWIn.aln', output_tree_file = 'CWin.dnd' ):
    """ purpose: To find the best multiple alignment given a file of FASTA sequences
        create the tree(.dnd) and the alignments as FASTA sequences(.aln)
    """
    cline = MultipleAlignCL( input_file )
    #creates command line for writing to output_file, in the order sequences were input
    #as separate FASTA-like sequences
    cline.set_output( output_file, output_order='INPUT', output_type = 'PIR' )
    cline.set_new_guide_tree( output_tree_file )
    clear_file = open( output_file, 'w' )   
    clear_file.close()
    #Clustalw module checks for existence of output file before writing, need previous two lines
    Bio.Clustalw.do_alignment( cline )

def Fasta_Iter_From_File( the_file ):
    """ http://www.ncbi.nlm.nih.gov/entrez/query/static/linking.html
        code base on #page 17 and 18 of the BioPython tutorial
    """
    file_for_blast = open( the_file,'r' )
    return Fasta.Iterator( file_for_blast )

def Next_Seq(iter):
    return iter.next()

def Append_Unique_Protein_Fasta( gi, out_file = 'AUPF.txt', format = 'Text' ):
    """ Purpose: Using 'gi' as a unique index to a protein, append to a
        file FASTA information from NCBI Entrez
        Text is the default to make file processing faster
        page 17 and 18 of the BioPython tutorial
    """
    result_handle = NCBI.query( format, 'Protein', doptcmdl = 'FASTA', uid = gi )
    result_file = open( out_file, 'a' )
    result_file.write( result_handle.read() )
    result_file.close()

def Begin_Clustalw_File(sequence, out_file):
    """ Write the opening sequence to the out file """
    clear_file = open( out_file,'w' )   #clear output file
    clear_file.write( ">gi|QUERY||| Original Sequence\n" )  #Write header
    lines = (len( sequence )-1) / 70 + 1
    for i in range(lines):
        integer = int(i)*70
        clear_file.write(sequence[integer:integer+70]+"\n")
    clear_file.write( "\n" )
    clear_file.close()

def Separate_Extension( string_file ):
    """ Given a string for a path name, separate the front from the extension
        return both [front, extension ]
    """
    copy_out_index = string_file.rfind(".")
    slash_index = string_file.rfind( os.sep )
    if(copy_out_index == -1 or copy_out_index < slash_index):
        copy_out_index = len( string_file )
    copy_out = string_file[:copy_out_index]
    extension = string_file[copy_out_index:]
    return copy_out, extension

def Get_Unique_Protein_Fasta( gi, out_file = 'UPF.txt', format = 'Text' ):
    """ Purpose: Using 'gi' as a unique index to a protein, create a
        file with FASTA information from NCBI Entrez
        Text is the default to make file processing faster
        page 17 and 18 of the BioPython tutorial
    """
    result_handle = NCBI.query( format, 'Protein', doptcmdl = 'FASTA', uid = gi )
    result_file = open( out_file, 'w' )
    result_file.write( result_handle.read() )
    result_file.close()

def Clustalw_Protein( infile = 'CWin.txt'):
    """ Create a protein distance matrix using clustalw """
    sys.path.append(os.getcwd())
    infile = global_functions.translate_filename_to_DOS_8_3_format(infile)
    command = "clustalw.exe %s -tree -outputtree=dist"%(infile)
    os.system(command)

def Bridge_Fasta_Header_And_Aligned(fasta_file, aligned_file, output_file):
    """ Given a non-aligned fasta file with header information, and an aligned file with gi numbers
        create a new file which has the aligned sequences with the fasta headers.
    """
    if( fasta_file == aligned_file ):
        print "fasta file same as aligned"
        return
    if( aligned_file == output_file ):
        print "aligned file same as output"
        return
    if( fasta_file == output_file ):
        print "fasta file same as output"
        return
    #create in program dictionary on GI's with text and sequence
    #aligned_file = aligned sequences but not the titles, PIR
    #fasta_file - Non-aligned sequences
    reader = open( fasta_file, 'r' )
    parsed_file = {}
    #initialize dictionary with GI and titles
    l = reader.readline( )
    while( l != "" ):
        if( l[0] == '>' ):
            gi, title = Grab_GI_Title( l )
            parsed_file[gi] =  l
        l = reader.readline( )
    reader.close( )
    #open aligned file and get sequences
    writer = open( output_file, 'w' )
    reader = open( aligned_file, 'r' )
    l = reader.readline( )
    while( l != "" ):
        gi, title = Grab_GI_Title( l )
        reader.readline( )  #blank line after header
        l, total_sequence = Grab_Sequence( reader )
        title = parsed_file[gi]
        writer.write(title)
        writer.write(total_sequence)
        writer.write("\n\n")
    reader.close()
    writer.close()
    
#
def Grab_GI_Title( line ):
    """ given line = fasta header line, extract a title """
    line = line.replace( ">", "" )
    individuals = string.split( line, '|' )
    gin = ""
    title = ""
    if( len( individuals ) > 1 ):
        gin = individuals[1]
        title = individuals[ len( individuals ) - 1 ].strip("\n ")
    #if( rest.find(' ') != -1 ):
    #    rest,title = string.split(rest,' ',1)
    #    title = title.replace("\n",'')
    return gin, title

def Grab_Sequence( reader ):
    """ given reader is the position after a fasta header, extract a sequence
        return the last line read and the sequence
    """
    #read and concatenate lines until > found or other non-sequence character found
    total_sequence = ''
    sequence = reader.readline( )
    while( sequence != '' and sequence.find( '>' ) == -1 ):
        total_sequence = total_sequence + sequence
        sequence = reader.readline()
    total_sequence = total_sequence.replace( '\n', '' )
    total_sequence = total_sequence.replace( '*', '' )
    return sequence, total_sequence

def Split_Sequences( fasta_file ):
    """ Given a fasta_file
        Take the first sequence, and find where the letters are
        Create strings of the proteins from subsequent sequences at the same position
    """
    reader = open( fasta_file, 'r' )
    l = reader.readline()
    if( l == "" ):
        return
    gi, title = Grab_GI_Title( l )
    l, total_sequence = Grab_Sequence( reader )
    prot_list = []
    prot_index = []
    for i in range(len(total_sequence)):
        if total_sequence[i:i+1] == '-':
            continue
        else:
            prot_index.append(i)
            prot_list.append(total_sequence[i:i+1])
    while( l != "" ):
        gi, title = Grab_GI_Title( l )
        l, total_sequence = Grab_Sequence( reader )
        for i in range( len ( prot_index ) ):
            id = prot_index[i]
            prot_list[i] = prot_list[i] + total_sequence[ id: id+1 ]
    reader.close()
    return prot_list
    