import RtkQueryGate from '@root/components/RtkQueryGate';
import {useGetSnowboardsQuery} from '@root/features/snowboards/api';
import {
  CellContext,
  ColumnDefTemplate,
  createColumnHelper,
  flexRender,
  getCoreRowModel,
  useReactTable,
} from '@tanstack/react-table';
import {Snowboard} from '@root/features/snowboards/types';
import './SnowboardsListPage.css';
import {useNavigate} from 'react-router-dom';
import {snowboardPath} from '@root/paths';

const ListActions: ColumnDefTemplate<CellContext<Snowboard, number>> = (
  props
) => {
  const navigate = useNavigate();
  return (
    <div>
      <button
        onClick={() => {
          navigate(snowboardPath({id: props.row.original.id.toString()}));
        }}
      >
        Update
      </button>
    </div>
  );
};

const columnHelper = createColumnHelper<Snowboard>();

const columns = [
  columnHelper.accessor('brand', {
    header: () => 'Brand',
    cell: (info) => info.getValue(),
    footer: (info) => info.column.id,
  }),
  columnHelper.accessor('model', {
    header: () => 'Model',
    cell: (info) => info.getValue(),
    footer: (info) => info.column.id,
  }),
  columnHelper.accessor('type', {
    header: () => 'Type',
    cell: (info) => info.getValue(),
    footer: (info) => info.column.id,
  }),
  columnHelper.accessor('id', {
    header: () => '',
    cell: ListActions,
    footer: (info) => info.column.id,
  }),
];

const SnowboardsListPage = () => {
  const queryOutput = useGetSnowboardsQuery();

  const table = useReactTable({
    data: queryOutput.data || [],
    columns,
    getCoreRowModel: getCoreRowModel(),
  });

  return (
    <RtkQueryGate {...queryOutput}>
      <div className="SnowboardList">
        <table>
          <thead>
            {table.getHeaderGroups().map((headerGroup) => (
              <tr key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <th key={header.id}>
                    {header.isPlaceholder
                      ? null
                      : flexRender(
                          header.column.columnDef.header,
                          header.getContext()
                        )}
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody>
            {table.getRowModel().rows.map((row) => (
              <tr key={row.id}>
                {row.getVisibleCells().map((cell) => (
                  <td key={cell.id}>
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </RtkQueryGate>
  );
};

export default SnowboardsListPage;
