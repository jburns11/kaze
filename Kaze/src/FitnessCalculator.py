import re
import math
from scipy.stats import pearsonr
from scipy import mean


class FitnessCalculator:
    """Class to calculate fitness metrics for comparing logs."""

    ref_log_positions = []
    ref_log_positions_lines = []
    ref_log_offset = 0
    comp_log_positions = []
    comp_log_offset = 0

    def __init__(self, ref_log, test_blocks=[]):
        """
        Initialize FitnessCalculator.

        Parameters:
        - log_1: Path to the reference log.
        - test_blocks: List of blocks for testing.
        """
        self.test_blocks = test_blocks
        self.ref_log_positions = []
        self.ref_log_positions_lines = []
        self.ref_log = ref_log
        f1 = open(ref_log, "r")
        f1_lines = f1.read()
        self.ref_log_positions_lines = re.findall(
            "\d+.\d+ \d+ NPS_SPEED_POS.*\n", f1_lines
        )
        for line in self.ref_log_positions_lines:
            line_split = line.split()
            self.ref_log_positions.append(
                [
                    float(line_split[0]),
                    float(line_split[9]),
                    float(line_split[10]),
                    float(line_split[11]),
                ]
            )
        self.comp_log_offset = 0

    def set_comp_log(self, log_2):
        """
        Set comparison log.

        Parameters:
        - log_2: Path to the comparison log.
        """
        self.comp_log_positions = []
        self.comp_log_positions_lines = []
        f1 = open(log_2, "r")
        f1_lines = f1.read()
        self.comp_log_positions_lines = re.findall(
            "\d+.\d+ \d+ NPS_SPEED_POS.*\n", f1_lines
        )
        for line in self.comp_log_positions_lines:
            line_split = line.split()
            self.comp_log_positions.append(
                [
                    float(line_split[0]),
                    float(line_split[9]),
                    float(line_split[10]),
                    float(line_split[11]),
                ]
            )

    def offset_position_pcc(self, log_1_offset, log_2_offset):
        """
        Calculate Pearson correlation coefficient between positions with offsets.

        Parameters:
        - log_1_offset: Offset for reference log.
        - log_2_offset: Offset for comparison log.

        Returns:
        - Pearson correlation coefficient.
        """
        window = min(
            200,
            min(
                len(self.ref_log_positions) - log_1_offset,
                len(self.comp_log_positions) - log_2_offset,
            ),
        )
        x_positions_1 = list(
            map(
                lambda a: a[1],
                self.ref_log_positions[log_1_offset : window + log_1_offset],
            )
        )
        x_positions_2 = list(
            map(
                lambda a: a[1],
                self.comp_log_positions[log_2_offset : window + log_2_offset],
            )
        )
        y_positions_1 = list(
            map(
                lambda a: a[2],
                self.ref_log_positions[log_1_offset : window + log_1_offset],
            )
        )
        y_positions_2 = list(
            map(
                lambda a: a[2],
                self.comp_log_positions[log_2_offset : window + log_2_offset],
            )
        )
        z_positions_1 = list(
            map(
                lambda a: a[3],
                self.ref_log_positions[log_1_offset : window + log_1_offset],
            )
        )
        z_positions_2 = list(
            map(
                lambda a: a[3],
                self.comp_log_positions[log_2_offset : window + log_2_offset],
            )
        )
        return (
            pearsonr(x_positions_1, x_positions_2)[0]
            + pearsonr(y_positions_1, y_positions_2)[0]
            + pearsonr(z_positions_1, z_positions_2)[0]
        ) / 3

    def position_pcc(self):
        """
        Calculate Pearson correlation coefficient between positions.

        Returns:
        - Pearson correlation coefficient.
        """
        length = min(
            len(self.ref_log_positions[self.ref_log_offset :]),
            len(self.comp_log_positions[self.comp_log_offset :]),
        )
        x_position_1 = list(
            map(
                lambda a: a[1],
                self.ref_log_positions[
                    self.ref_log_offset : self.ref_log_offset + length
                ],
            )
        )
        x_position_2 = list(
            map(
                lambda a: a[1],
                self.comp_log_positions[
                    self.comp_log_offset : self.comp_log_offset + length
                ],
            )
        )
        y_position_1 = list(
            map(
                lambda a: a[2],
                self.ref_log_positions[
                    self.ref_log_offset : self.ref_log_offset + length
                ],
            )
        )
        y_position_2 = list(
            map(
                lambda a: a[2],
                self.comp_log_positions[
                    self.comp_log_offset : self.comp_log_offset + length
                ],
            )
        )
        z_position_1 = list(
            map(
                lambda a: a[3],
                self.ref_log_positions[
                    self.ref_log_offset : self.ref_log_offset + length
                ],
            )
        )
        z_position_2 = list(
            map(
                lambda a: a[3],
                self.comp_log_positions[
                    self.comp_log_offset : self.comp_log_offset + length
                ],
            )
        )
        return (
            pearsonr(x_position_1, x_position_2)[0]
            + pearsonr(y_position_1, y_position_2)[0]
            + pearsonr(z_position_1, z_position_2)[0]
        ) / 3

    def block_position_pcc(self, block_1, block_2):
        """
        Calculate Pearson correlation coefficient between positions in blocks.

        Parameters:
        - block_1: Reference block.
        - block_2: Comparison block.

        Returns:
        - Pearson correlation coefficient.
        """
        length = min(len(block_1), len(block_2))
        x_position_1 = list(map(lambda a: a[1], block_1[0:length]))
        x_position_2 = list(map(lambda a: a[1], block_2[0:length]))
        y_position_1 = list(map(lambda a: a[2], block_1[0:length]))
        y_position_2 = list(map(lambda a: a[2], block_2[0:length]))
        z_position_1 = list(map(lambda a: a[3], block_1[0:length]))
        z_position_2 = list(map(lambda a: a[3], block_2[0:length]))

        diff = []
        for i in range(length):
            diff.append(
                -1
                * math.sqrt(
                    (x_position_1[i] - x_position_2[i]) ** 2
                    + (y_position_1[i] - y_position_2[i]) ** 2
                    + (z_position_1[i] - z_position_2[i]) ** 2
                )
            )

        return mean(diff)

    def out_of_bound(self, bound, position):
        """
        Check if a position is out of bounds.

        Parameters:
        - bound: Boundary coordinates.
        - position: Position coordinates.

        Returns:
        - Boolean indicating if position is out of bounds.
        """
        if position[2] >= bound[0][0] and position[2] <= bound[1][0]:
            if position[1] > bound[0][1] and position[1] <= bound[1][1]:
                return True
        return False

    def calc_out_of_bounds(self):
        """
        Calculate if positions are out of bounds.

        Returns:
        - Boolean indicating if any position is out of bounds.
        """
        for pos in self.comp_log_positions:
            if pos[2] <= -10 and pos[1] <= 30:
                return True

            elif pos[2] <= -10 and pos[1] >= 50:
                return True

            elif pos[2] >= 10 and pos[1] >= 50:
                return True

            elif pos[2] >= 10 and pos[1] <= 30:
                return True

            elif pos[2] <= -50 or pos[2] >= 50:
                return True

            elif pos[1] <= -10 or pos[1] >= 90:
                return True

        return False

    def calc_pcc_with_best_offset(self, log_2):
        """
        Calculate Pearson correlation coefficient with best offset.

        Parameters:
        - log_2: Path to the comparison log.

        Returns:
        - Tuple containing Pearson correlation coefficient and out of bounds boolean.
        """
        self.set_comp_log(log_2)
        correlations = []
        max_frames = min(
            200, min(len(self.ref_log_positions), len(self.comp_log_positions))
        )
        for i in range(max_frames):
            correlations.append([(0, i), (self.offset_position_pcc(0, i))])
            correlations.append([(i, 0), (self.offset_position_pcc(i, 0))])
            m = correlations[0]
            for i in correlations:
                if i[1] > m[1]:
                    m = i
                self.ref_log_offset = m[0][0]
                self.comp_log_offset = m[0][1]
        return (self.position_pcc(), self.calc_out_of_bounds())

    def calc_pcc_per_block(self, log_2):
        """
        Calculate Pearson correlation coefficient per block.

        Parameters:
        - log_2: Path to the comparison log.

        Returns:
        - List of Pearson correlation coefficients.
        """
        ref_positions = dict()
        comp_positions = dict()
        block_pccs = []
        for i in self.test_blocks:
            ref_positions[i[1]] = []
            comp_positions[i[1]] = []

        curr_block_i = 0

        f = open(self.ref_log)
        for line in f.readlines():
            if "ROTORCRAFT_NAV_STATUS" in line:
                curr_block_i = int(line.split()[7])
            if "NPS_SPEED_POS" in line:
                for test_block in self.test_blocks:
                    if curr_block_i == test_block[1]:
                        line_split = line.split()
                        ref_positions[curr_block_i].append(
                            [
                                float(line_split[0]),
                                float(line_split[9]),
                                float(line_split[10]),
                                float(line_split[11]),
                            ]
                        )

        f2 = open(log_2)
        curr_block_i = 0
        for line in f2.readlines():
            if "ROTORCRAFT_NAV_STATUS" in line:
                curr_block_i = int(line.split()[7])
            if "NPS_SPEED_POS" in line:
                for test_block in self.test_blocks:
                    if curr_block_i == test_block[1]:
                        line_split = line.split()
                        comp_positions[curr_block_i].append(
                            [
                                float(line_split[0]),
                                float(line_split[9]),
                                float(line_split[10]),
                                float(line_split[11]),
                            ]
                        )

        for i in self.test_blocks:
            if len(comp_positions[i[1]]) != 0 and len(ref_positions[i[1]]) != 0:
                pcc = self.block_position_pcc(ref_positions[i[1]], comp_positions[i[1]])
                block_pccs.append(pcc)
            else:
                return [1] * len(self.test_blocks)

        return block_pccs
