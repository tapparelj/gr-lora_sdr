# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
#
import filecmp
import os
import sys
import re
from file_writer import file_writer


def main():
    """[summary]
    """
    print("Welcome to the test cases and reference file generator of LoRa SDR\n")

    # below is a list of values to generate tx and rx test cases for
    source_data_list = [
        "PKdhtXMmr18n2L9K88eMlGn7CcctT9RwKSB1FebW397VI5uG1yhc3uavuaOb9vyJ"]
    bw_list = [250000]
    sf_list = [7, 8,9,10,11,12]
    paylen_list = [64]
    impl_head_list = [True, False]
    has_crc_list = [False, True]
    cr_list = [0,5,6,7,8]

    # start test counter at 1
    test_counter = 1
    file_writer.write_cmake_begin()
    
    # loop over all values and make the test cases and the reference file
    for source_data in source_data_list:
        for bw in bw_list:
            for sf in sf_list:
                for paylen in paylen_list:
                    for impl_head in impl_head_list:
                        for has_crc in has_crc_list:
                            for cr in cr_list:

                                file_writer.clean_template(test_counter)

                                print("Generating test case {}".format(
                                    test_counter))
                                print("file: {0} source: {1} bw: {2} sf: {3} paylen: {4} impl: {5} crc: {6} cr: {7}".format(
                                    test_counter, source_data, bw, sf, paylen, impl_head, has_crc, cr))

                                # write info into test case template
                                file_writer.write_template(
                                    test_counter, source_data, bw, sf, paylen, impl_head, has_crc, cr)

                                file_writer.update_cmake(test_counter)

                                test_counter = test_counter+1

main()